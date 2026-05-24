# 📓 LLM Benchmark Logbook

## [2026-05-24] - Bare-Metal GPU İlk Otomasyon Testi
- **Test Edilen Donanım:** Ryzen 5 5600 | 64GB RAM | RX 6900 XT 16GB VRAM
- **Sürücü Katmanı:** Ubuntu Desktop + Resmi ROCm (HSA_OVERRIDE_GFX_VERSION=10.3.0)
- **Amaç:** Model bazlı Token/s kararlılığını ve CPU/GPU offload sınırlarını ölçmek.

### Gözlemler ve Notlar
* `/etc/systemd/system/ollama.service.d/override.conf` ayarı kalıcı hale getirildikten sonra port kilitlenmeleri çözüldü.
* Tamamen VRAM'e sığan 8B modellerin (Gemma 2 / Llama 3) anlık tepki süresi (TTFT) muazzam seviyede.
* `benchmark_results.csv` üzerinden model karşılaştırmaları (Qwen vs Gemma) bu dökümana işlenecektir.