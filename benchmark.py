import json
import time
import csv
import requests
import os
import subprocess
import sys
from datetime import datetime

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_PS_URL = "http://localhost:11434/api/ps"
DEFAULT_MODEL = "gemma4:latest"

def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_local_models():
    """Ollama API'sinden yerel olarak yüklü modelleri çeker (embedding modellerini filtreler)."""
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            # embed kelimesi içeren modelleri filtreleyelim (örn: nomic-embed-text)
            generative_models = [m for m in models if "embed" not in m.lower()]
            return generative_models
    except Exception as e:
        print(f"⚠️ Ollama model listesi alınamadı (Ollama çalışıyor mu?): {e}")
    return []

def get_loaded_model_info(model_name):
    """Ollama API'sinden o an yüklü olan modelin donanım/bellek ve işlemci dağılım bilgilerini çeker."""
    try:
        response = requests.get(OLLAMA_PS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for m in data.get("models", []):
                if m["name"] == model_name or m["model"] == model_name:
                    details = m.get("details", {})
                    size = m.get("size", 0)
                    size_vram = m.get("size_vram", 0)
                    size_gb = round(size / (1024**3), 2)
                    vram_gb = round(size_vram / (1024**3), 2)
                    
                    # İşlemci dağılımını hesaplama (Ollama resmi CLI mantığı)
                    if size_vram == 0:
                        processor = "100% CPU"
                    elif size_vram == size:
                        processor = "100% GPU"
                    elif size_vram > size or size == 0:
                        processor = "Bilinmiyor"
                    else:
                        size_cpu = size - size_vram
                        cpu_percent = round((size_cpu / size) * 100)
                        processor = f"{cpu_percent}%/{100 - cpu_percent}% CPU/GPU"
                        
                    return {
                        "param_size": details.get("parameter_size", "Bilinmiyor"),
                        "quantization": details.get("quantization_level", "Bilinmiyor"),
                        "model_size_gb": size_gb,
                        "vram_usage_gb": vram_gb,
                        "processor": processor
                    }
    except Exception as e:
        print(f"⚠️ Ollama PS bilgisi alınamadı: {e}")
    
    return {
        "param_size": "Bilinmiyor",
        "quantization": "Bilinmiyor",
        "model_size_gb": 0.0,
        "vram_usage_gb": 0.0,
        "processor": "Bilinmiyor"
    }

def get_cpu_info():
    """Sistemden CPU model bilgisini çekmeye çalışır."""
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line.lower():
                        return line.split(":")[1].strip()
    except Exception:
        pass
    return "Bilinmiyor"

def get_gpu_info():
    """Sistemden GPU model bilgisini çekmeye çalışır."""
    try:
        result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if any(x in line.lower() for x in ["vga", "3d", "display"]) and "amd" in line.lower():
                    if "[" in line and "]" in line:
                        gpu_name = line.split("[")[-1].split("]")[0]
                        return f"AMD {gpu_name}"
                    return line.split(":")[-1].strip()
    except Exception:
        pass
    return "Bilinmiyor"

def select_model(models):
    """Kullanıcıya mevcut modelleri listeleyip birini seçtirir ya da hepsini seçme seçeneği sunar."""
    if not models:
        print("⚠️ Ollama üzerinde yüklü model bulunamadı veya Ollama'ya bağlanılamadı.")
        manual = input(f"Test etmek istediğiniz model adını manuel girin (Varsayılan: {DEFAULT_MODEL}): ").strip()
        return [manual] if manual else [DEFAULT_MODEL]
    
    print("\n📦 Ollama Üzerindeki Mevcut Modeller:")
    for idx, model in enumerate(models, 1):
        print(f"  [{idx}] {model}")
    all_option_idx = len(models) + 1
    print(f"  [{all_option_idx}] TÜM MODELLERİ SIRAYLA ÇALIŞTIR")
    
    while True:
        try:
            choice = input(f"\nLütfen test etmek istediğiniz modelin numarasını seçin (1-{all_option_idx}): ").strip()
            if not choice:
                print(f"Varsayılan model seçildi: {models[0]}")
                return [models[0]]
            choice_idx = int(choice) - 1
            if choice_idx == len(models):
                print("📢 Seçim: Tüm modeller sırayla çalıştırılacak.")
                return models
            elif 0 <= choice_idx < len(models):
                return [models[choice_idx]]
            else:
                print(f"Lütfen 1 ile {all_option_idx} arasında bir sayı girin.")
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")

def get_model_params(model_name, category):
    """Belirli bir model için top_p, top_k ve thinking_active (düşünme modu) ayarlarını döner."""
    # Varsayılan değerler (Standart Llama/Qwen)
    top_p = 0.90
    top_k = 40
    thinking_active = False
    
    model_lower = model_name.lower()
    
    # Gemma 4 serisi ise
    if "gemma4" in model_lower:
        top_p = 0.95
        top_k = 64
        # Akıl yürütme (Reasoning) ve Kod yazma (Reasoning/Coding) sorularında düşünme modunu etkinleştir
        if category in ["Reasoning", "Reasoning/Coding"]:
            thinking_active = True
            
    # DeepSeek R1 serisi ise
    elif "r1" in model_lower:
        # DeepSeek R1 modellerinde düşünme (reasoning) yerleşiktir
        thinking_active = True
        
    return top_p, top_k, thinking_active

def run_benchmark(model_name, csv_file="benchmark_results.csv", timeout=300):
    questions = load_questions()
    results = []
    
    cpu_info = get_cpu_info()
    gpu_info = get_gpu_info()
    print(f"🚀 Benchmark başlatıldı! Test edilen model: {model_name}")
    print(f"🖥️  Sistem Donanımı: CPU: {cpu_info} | GPU: {gpu_info}\n" + "-"*50)
    
    model_info = None
    
    for q in questions:
        print(f"⏳ [{q['id']}] {q['category']} testi koşuluyor...")
        
        top_p, top_k, thinking_active = get_model_params(model_name, q["category"])
        
        payload = {
            "model": model_name,
            "prompt": q["prompt"],
            "stream": False,
            "options": {
                "temperature": q["temperature"],
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": 2048
            }
        }
        
        if thinking_active and "gemma4" in model_name.lower():
            payload["system"] = "<|think|>"
        
        start_time = time.time()
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Model bilgilerini ilk başarılı yanıttan sonra çekiyoruz (belleğe yüklendiği kesinleştiğinde)
                if model_info is None:
                    model_info = get_loaded_model_info(model_name)
                    print(f"ℹ️ Model Bilgileri (Ollama PS): Parametre: {model_info['param_size']} | Quant: {model_info['quantization']} | Model Boyutu: {model_info['model_size_gb']} GB | VRAM Kullanımı: {model_info['vram_usage_gb']} GB | İşlemci: {model_info['processor']}")
                
                # Ollama nanosaniye cinsinden süreler döner. Yoksa Python time fallback kullanılır.
                total_duration_ns = data.get("total_duration", 0)
                eval_duration_ns = data.get("eval_duration", 0)
                eval_count = data.get("eval_count", 0)
                
                # Toplam süre (saniye)
                if total_duration_ns > 0:
                    duration_sec = total_duration_ns / 1e9
                else:
                    duration_sec = end_time - start_time
                
                # Eğer eval_count dönmediyse tahmini bir değer alalım
                if eval_count == 0:
                    eval_count = len(data.get("response", "").split()) * 1.3
                
                # Üretim hızı (Token/s) - Ağ gecikmesinden bağımsız gerçek üretim hızı için eval_duration kullanılır
                if eval_duration_ns > 0:
                    tokens_per_second = eval_count / (eval_duration_ns / 1e9)
                else:
                    tokens_per_second = eval_count / duration_sec if duration_sec > 0 else 0
                
                result = {
                    "id": q["id"],
                    "category": q["category"],
                    "temperature": q["temperature"],
                    "top_p": top_p,
                    "top_k": top_k,
                    "thinking_active": thinking_active,
                    "duration_sec": round(duration_sec, 2),
                    "tokens_produced": eval_count,
                    "tokens_per_sec": round(tokens_per_second, 2),
                    "response_preview": data.get("response", "")[:100].replace("\n", " ") + "..."
                }
                results.append(result)
                print(f"✅ Tamamlandı: {result['tokens_per_sec']} T/s | Süre: {result['duration_sec']} sn\n")
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]
                except Exception:
                    pass
                print(f"❌ Hata: API {response.status_code} kodu döndürdü. Detay: {error_msg}")
                result = {
                    "id": q["id"],
                    "category": q["category"],
                    "temperature": q["temperature"],
                    "top_p": top_p,
                    "top_k": top_k,
                    "thinking_active": thinking_active,
                    "duration_sec": 0.0,
                    "tokens_produced": 0,
                    "tokens_per_sec": 0.0,
                    "response_preview": f"HATA: API {response.status_code} - {error_msg[:100]}"
                }
                results.append(result)
        except requests.exceptions.Timeout:
            timeout_str = f"{timeout}sn" if timeout is not None else "Sınırsız"
            print(f"❌ Zaman Aşımı Hatası: Model {timeout_str} içinde yanıt vermedi. (Base model veya büyük model olabilir)")
            if "-base" in model_name:
                print("⚠️  İpucu: Base modeller (sohbet eğitimi almamış olanlar) soruya cevap vermek yerine sonsuza kadar devam metni üretmeye çalışabilirler.")
            result = {
                "id": q["id"],
                "category": q["category"],
                "temperature": q["temperature"],
                "top_p": top_p,
                "top_k": top_k,
                "thinking_active": thinking_active,
                "duration_sec": float(timeout) if timeout is not None else 0.0,
                "tokens_produced": 0,
                "tokens_per_sec": 0.0,
                "response_preview": f"HATA: {timeout_str} Zaman Aşımı (Timeout) - Model yanıt vermedi."
            }
            results.append(result)
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {str(e)}")
            result = {
                "id": q["id"],
                "category": q["category"],
                "temperature": q["temperature"],
                "top_p": top_p,
                "top_k": top_k,
                "thinking_active": thinking_active,
                "duration_sec": 0.0,
                "tokens_produced": 0,
                "tokens_per_sec": 0.0,
                "response_preview": f"HATA: Bağlantı Hatası ({str(e)})"
            }
            results.append(result)
            
    # Eğer hiç başarılı istek yapılamadıysa varsayılan değerlerle kaydet
    if model_info is None:
        model_info = {
            "param_size": "Bilinmiyor",
            "quantization": "Bilinmiyor",
            "model_size_gb": 0.0,
            "vram_usage_gb": 0.0,
            "processor": "Bilinmiyor"
        }
            
    save_results(model_name, model_info, cpu_info, gpu_info, results, csv_file)
    if csv_file != "benchmark_results.csv":
        save_results(model_name, model_info, cpu_info, gpu_info, results, "benchmark_results.csv")

def save_results(model_name, model_info, cpu_info, gpu_info, results, csv_file="benchmark_results.csv"):
    fields = [
        "timestamp",
        "model_name", 
        "param_size", 
        "quantization", 
        "model_size_gb", 
        "vram_usage_gb", 
        "processor",
        "cpu_info",
        "gpu_info",
        "id", 
        "category", 
        "temperature", 
        "top_p",
        "top_k",
        "thinking_active",
        "duration_sec", 
        "tokens_produced", 
        "tokens_per_sec", 
        "response_preview"
    ]
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Her sonuca model ismini, donanım, bellek ve işlemci bilgilerini ekle
    for r in results:
        r["timestamp"] = current_time
        r["model_name"] = model_name
        r["param_size"] = model_info["param_size"]
        r["quantization"] = model_info["quantization"]
        r["model_size_gb"] = model_info["model_size_gb"]
        r["vram_usage_gb"] = model_info["vram_usage_gb"]
        r["processor"] = model_info["processor"]
        r["cpu_info"] = cpu_info
        r["gpu_info"] = gpu_info

    file_exists = os.path.isfile(csv_file)
    upgrade_needed = False
    existing_rows = []

    if file_exists:
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames:
                    # Eksik alanları kontrol et
                    missing_fields = [field for field in fields if field not in reader.fieldnames]
                    if missing_fields:
                        upgrade_needed = True
                        for row in reader:
                            # model_name yoksa ekle (en eski testler için)
                            if "model_name" not in row:
                                row["model_name"] = "gemma4:latest"
                            
                            # Bilinen eski modeller için donanım/bellek bilgilerini eşleştir
                            if row["model_name"] == "gemma4:latest":
                                row["param_size"] = "8.0B"
                                row["quantization"] = "Q4_K_M"
                                row["model_size_gb"] = 8.95
                                row["vram_usage_gb"] = 8.95
                                row["processor"] = "100% GPU"
                            elif row["model_name"] == "llama3.2:3b":
                                row["param_size"] = "3.2B"
                                row["quantization"] = "Q4_K_M"
                                row["model_size_gb"] = 1.88
                                row["vram_usage_gb"] = 1.88
                                row["processor"] = "100% GPU"
                            
                            # Eski satırların CPU/GPU bilgilerini logbook'taki Ryzen 5 5600 ve RX 6900 XT donanımlarıyla eşleştiriyoruz
                            if "cpu_info" not in row or row["cpu_info"] in [None, "", "Bilinmiyor"]:
                                row["cpu_info"] = "AMD Ryzen 5 5600 6-Core Processor"
                            if "gpu_info" not in row or row["gpu_info"] in [None, "", "Bilinmiyor"]:
                                row["gpu_info"] = "AMD Radeon RX 6800/6800 XT / 6900 XT"
                            if "processor" not in row or row["processor"] in [None, "", "Bilinmiyor"]:
                                row["processor"] = "100% GPU"
                            
                            # Kalan tüm eksik alanları varsayılanlarla doldur
                            for mf in missing_fields:
                                if mf not in row:
                                    if mf in ["model_size_gb", "vram_usage_gb"]:
                                        row[mf] = 0.0
                                    else:
                                        row[mf] = "Bilinmiyor"
                            existing_rows.append(row)
        except Exception as e:
            print(f"⚠️ Eski CSV okunurken hata oluştu, yeni dosya oluşturulacak: {e}")
            file_exists = False

    if upgrade_needed:
        print("🔄 Eski CSV tespit edildi, yeni sütunlar eklenerek güncelleniyor...")
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(existing_rows)
        except Exception as e:
            print(f"⚠️ CSV güncelleme hatası: {e}")

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists and not upgrade_needed:
            writer.writeheader()
        writer.writerows(results)
    print(f"📊 Tüm sonuçlar başarıyla '{csv_file}' dosyasına kaydedildi!")

if __name__ == "__main__":
    models = get_local_models()
    selected_models = select_model(models)
    
    try:
        timeout_input = input("\n⏱️  Zaman aşımı (timeout) süresini saniye cinsinden girin (Varsayılan: 300, Sınırsız için 0): ").strip()
        timeout = int(timeout_input) if timeout_input else 300
        if timeout <= 0:
            timeout = None
    except ValueError:
        print("⚠️ Geçersiz değer. Varsayılan olarak 300 saniye kullanılacak.")
        timeout = 300
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"benchmark_results_{timestamp}.csv"
    
    total_models = len(selected_models)
    for index, model in enumerate(selected_models, 1):
        timeout_desc = f"{timeout} sn" if timeout is not None else "Sınırsız"
        print(f"\n🚀 [{index}/{total_models}] {model} modeli için benchmark başlıyor... (Zaman Aşımı: {timeout_desc})")
        run_benchmark(model, csv_file, timeout=timeout)
        print(f"✨ {model} benchmarkı tamamlandı.\n" + "="*50)

    print("\n📊 Grafiklerin otomatik üretimi başlatılıyor...")
    try:
        # visualize_benchmark.py ve visualize_all.py scriptlerini çalıştırıyoruz.
        # Bu scriptler varsayılan olarak güncellenen master benchmark_results.csv üzerinden çizim yapacaktır.
        subprocess.run([sys.executable, "visualize_benchmark.py"], check=True)
        subprocess.run([sys.executable, "visualize_all.py"], check=True)
        print("🎉 Tüm analiz grafikleri başarıyla güncellendi!")
    except Exception as e:
        print(f"⚠️ Grafik çizimi sırasında bir hata oluştu: {e}")