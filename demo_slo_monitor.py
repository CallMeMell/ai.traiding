"""
demo_slo_monitor.py - SLO Monitor Demo
======================================
Demonstriert die Verwendung des SLO Monitors wie im Issue beschrieben.
"""

from automation.slo_monitor import SLOMonitor

# SLO-Monitor Beispiel wie im Issue beschrieben
print("=" * 70)
print("SLO Monitor - Demo")
print("=" * 70)

# Monitor erstellen
monitor = SLOMonitor()
print("\n✓ SLOMonitor erstellt")

# Error-Rate prüfen
print("\n📊 Checking error rate...")
monitor.check_error_rate()

# Render-Zeit prüfen
print("\n📊 Checking render time...")
monitor.check_render_time()

# Schwellenwert anpassen
print("\n⚙️  Anpassen des error_rate_threshold...")
monitor.error_rate_threshold = 0.05
print(f"✓ error_rate_threshold = {monitor.error_rate_threshold}")

# Einige Messungen hinzufügen für Demo-Zwecke
print("\n📊 Hinzufügen von Messungen für Demo...")
for i in range(100):
    # 98% Erfolgsquote
    monitor.add_error_measurement(success=(i < 98))
    # 96% unter Render-Zeit-Schwellenwert
    render_time = 400.0 if i < 96 else 600.0
    monitor.add_render_time_measurement(render_time)

print("✓ 100 Messungen hinzugefügt")

# Status erneut prüfen
print("\n📊 Erneute Prüfung nach Messungen...")
error_status = monitor.check_error_rate()
render_status = monitor.check_render_time()

print(f"\nError Rate: {error_status['status']} ({error_status['current_percentage']:.1f}%)")
print(f"Render Time: {render_status['status']} ({render_status['current_percentage']:.1f}%)")

# Alle Status abrufen
print("\n📊 Alle SLO Status abrufen...")
all_status = monitor.get_all_status()
print(f"✓ {len(all_status)} SLOs überwacht")

print("\n" + "=" * 70)
print("✅ Demo abgeschlossen!")
print("=" * 70)
print("\n💡 Tipp: Prüfe data/session/events.jsonl für needs-review Events")
