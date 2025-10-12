"""
test_auto_strategy_selection.py - Tests für automatische Strategie-Auswahl
==========================================================================

Tests für die automatische Strategie-Auswahl und Config-Update-Funktionalität
"""

import pytest
import os
import sys
import yaml
import pandas as pd
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy_selector import StrategySelector, StrategyScore
from utils import generate_sample_data


class TestAutoStrategySelection:
    """Tests für automatische Strategie-Auswahl"""
    
    def test_strategy_selector_auto_mode(self):
        """Test dass StrategySelector ohne Interaktion läuft"""
        # Generiere Daten
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        # Erstelle Selector
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5
        )
        
        # Führe Auswahl durch
        best_name, best_score = selector.run_selection(data)
        
        # Validiere Ergebnis
        assert best_name is not None
        assert isinstance(best_name, str)
        assert len(best_name) > 0
        
        assert isinstance(best_score, StrategyScore)
        assert best_score.score > 0
        assert best_score.total_trades >= 5
    
    def test_strategy_selector_results_storage(self):
        """Test dass Ergebnisse korrekt gespeichert werden"""
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5
        )
        
        best_name, best_score = selector.run_selection(data)
        
        # Check dass results gespeichert wurden
        assert len(selector.results) > 0
        assert best_name in selector.results
        
        # Check dass alle Strategien bewertet wurden
        for name, score in selector.results.items():
            assert isinstance(score, StrategyScore)
            assert score.total_trades >= 5
    
    def test_export_ranking_csv(self, tmp_path):
        """Test CSV Export der Rangliste"""
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5
        )
        
        best_name, best_score = selector.run_selection(data)
        
        # Export zu temporärer Datei
        export_path = tmp_path / "ranking.csv"
        selector.export_ranking(str(export_path))
        
        # Validiere dass Datei existiert
        assert export_path.exists()
        
        # Lade CSV und validiere Inhalt
        df = pd.read_csv(export_path)
        
        assert len(df) > 0
        assert 'strategy_name' in df.columns
        assert 'score' in df.columns
        assert 'roi' in df.columns
        assert 'sharpe_ratio' in df.columns
        assert 'win_rate' in df.columns
        
        # Check dass Scores sortiert sind (beste zuerst)
        scores = df['score'].tolist()
        assert scores == sorted(scores, reverse=True)
    
    def test_config_update_function(self, tmp_path):
        """Test Config-Update Funktion"""
        # Erstelle temporäre Config
        config_path = tmp_path / "live_risk.yaml"
        
        initial_config = {
            'pairs': 'BTCUSDT',
            'strategy': 'Old Strategy',
            'max_risk_per_trade': 0.005
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(initial_config, f)
        
        # Importiere Update-Funktion
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
        from auto_select_strategy import update_config_strategy
        
        # Update Strategie
        new_strategy = "RSI Conservative"
        success = update_config_strategy(new_strategy, str(config_path))
        
        assert success
        
        # Lade Config und validiere
        with open(config_path, 'r') as f:
            updated_config = yaml.safe_load(f)
        
        assert updated_config['strategy'] == new_strategy
        assert updated_config['pairs'] == 'BTCUSDT'
        assert updated_config['max_risk_per_trade'] == 0.005
    
    def test_config_update_creates_default(self, tmp_path):
        """Test dass Config erstellt wird wenn nicht vorhanden"""
        config_path = tmp_path / "new_config.yaml"
        
        # Importiere Update-Funktion
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
        from auto_select_strategy import update_config_strategy
        
        # Update Strategie (Config existiert nicht)
        new_strategy = "MA Crossover (10/30)"
        success = update_config_strategy(new_strategy, str(config_path))
        
        assert success
        assert config_path.exists()
        
        # Lade Config und validiere
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['strategy'] == new_strategy
        assert 'pairs' in config
        assert 'max_risk_per_trade' in config
    
    def test_min_trades_filter(self):
        """Test dass min_trades Filter funktioniert"""
        data = generate_sample_data(n_bars=300, start_price=30000)
        
        # Sehr hoher min_trades Threshold
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=50  # Sehr hoch
        )
        
        # Sollte trotzdem funktionieren oder Fehler werfen
        try:
            best_name, best_score = selector.run_selection(data)
            # Falls erfolgreich, check min_trades
            assert best_score.total_trades >= 50
        except ValueError as e:
            # Erwartet wenn keine Strategie Mindestanforderungen erfüllt
            assert "Keine gültigen Strategien" in str(e)
    
    def test_different_capital_sizes(self):
        """Test mit verschiedenen Kapitalgrößen"""
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        for capital in [1000, 10000, 100000]:
            selector = StrategySelector(
                initial_capital=capital,
                trade_size=100.0,
                min_trades=5
            )
            
            best_name, best_score = selector.run_selection(data)
            
            assert best_name is not None
            assert best_score.final_capital > capital * 0.5  # Min 50% erhaltung


class TestIntegrationScenarios:
    """Integration Tests für verschiedene Szenarien"""
    
    def test_full_workflow_with_export(self, tmp_path):
        """Test kompletter Workflow mit Export"""
        # Daten generieren
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        # Selector erstellen
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5
        )
        
        # Auswahl durchführen
        best_name, best_score = selector.run_selection(data)
        
        # Export Ranking
        ranking_path = tmp_path / "ranking.csv"
        selector.export_ranking(str(ranking_path))
        
        # Config aktualisieren
        config_path = tmp_path / "live_risk.yaml"
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
        from auto_select_strategy import update_config_strategy
        
        success = update_config_strategy(best_name, str(config_path))
        
        # Validiere alle Outputs
        assert ranking_path.exists()
        assert config_path.exists()
        assert success
        
        # Lade und validiere Config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['strategy'] == best_name
        
        # Lade und validiere Ranking
        df = pd.read_csv(ranking_path)
        assert len(df) > 0
        assert df.iloc[0]['strategy_name'] == best_name
    
    def test_strategy_persistence_across_runs(self, tmp_path):
        """Test dass Strategie über mehrere Läufe persistent ist"""
        config_path = tmp_path / "live_risk.yaml"
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
        from auto_select_strategy import update_config_strategy
        
        # Erster Lauf
        selector1 = StrategySelector(min_trades=5)
        best_name1, _ = selector1.run_selection(data)
        update_config_strategy(best_name1, str(config_path))
        
        # Zweiter Lauf mit anderen Parametern
        selector2 = StrategySelector(min_trades=3)
        best_name2, _ = selector2.run_selection(data)
        update_config_strategy(best_name2, str(config_path))
        
        # Lade finale Config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Strategy sollte auf den zweiten Lauf aktualisiert sein
        assert config['strategy'] == best_name2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
