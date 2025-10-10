"""
test_strategy_selector.py - Tests für automatische Strategie-Auswahl
====================================================================
"""

import pytest
import pandas as pd
import numpy as np
from strategy_selector import StrategySelector, StrategyScore
from utils import generate_sample_data


class TestStrategySelector:
    """Tests für StrategySelector Klasse"""
    
    def test_initialization(self):
        """Test Initialisierung mit Standard-Parametern"""
        selector = StrategySelector()
        
        assert selector.initial_capital == 10000.0
        assert selector.trade_size == 100.0
        assert selector.min_trades == 10
        assert 'roi' in selector.weights
        assert 'sharpe_ratio' in selector.weights
        assert 'calmar_ratio' in selector.weights
    
    def test_initialization_custom_weights(self):
        """Test Initialisierung mit benutzerdefinierten Gewichten"""
        custom_weights = {
            'roi': 0.5,
            'sharpe_ratio': 0.3,
            'calmar_ratio': 0.1,
            'win_rate': 0.05,
            'max_drawdown': 0.05
        }
        
        selector = StrategySelector(weights=custom_weights)
        assert selector.weights == custom_weights
    
    def test_setup_strategies(self):
        """Test Setup aller Strategien"""
        selector = StrategySelector()
        strategies = selector.setup_strategies()
        
        # Mindestens 5 Strategien sollten verfügbar sein
        assert len(strategies) >= 5
        
        # Prüfe dass Standardstrategien vorhanden sind
        assert 'Golden Cross (50/200)' in strategies
        assert 'MA Crossover (20/50)' in strategies
        assert 'RSI Mean Reversion' in strategies
    
    def test_calculate_score_perfect_strategy(self):
        """Test Score-Berechnung für perfekte Strategie"""
        selector = StrategySelector()
        
        # Perfekte Metriken
        metrics = {
            'roi': 100.0,
            'sharpe_ratio': 3.0,
            'calmar_ratio': 3.0,
            'win_rate': 100.0,
            'max_drawdown': 0.0
        }
        
        score = selector.calculate_score(metrics)
        
        # Score sollte nahe 100 sein
        assert score >= 95.0
        assert score <= 100.0
    
    def test_calculate_score_poor_strategy(self):
        """Test Score-Berechnung für schlechte Strategie"""
        selector = StrategySelector()
        
        # Schlechte Metriken
        metrics = {
            'roi': -20.0,
            'sharpe_ratio': -1.0,
            'calmar_ratio': -1.0,
            'win_rate': 20.0,
            'max_drawdown': -40.0
        }
        
        score = selector.calculate_score(metrics)
        
        # Score sollte niedrig sein
        assert score < 30.0
    
    def test_calculate_score_average_strategy(self):
        """Test Score-Berechnung für durchschnittliche Strategie"""
        selector = StrategySelector()
        
        # Durchschnittliche Metriken
        metrics = {
            'roi': 20.0,
            'sharpe_ratio': 1.0,
            'calmar_ratio': 1.0,
            'win_rate': 55.0,
            'max_drawdown': -10.0
        }
        
        score = selector.calculate_score(metrics)
        
        # Score sollte mittelmäßig sein
        assert score >= 40.0
        assert score <= 70.0
    
    def test_run_selection_with_sample_data(self):
        """Test komplette Strategie-Auswahl mit simulierten Daten"""
        # Generiere Test-Daten
        data = generate_sample_data(n_bars=500, start_price=30000)
        
        # Erstelle Selector mit niedrigerer Mindestanzahl
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5  # Niedriger für schnelleren Test
        )
        
        # Führe Auswahl durch
        best_name, best_score = selector.run_selection(data)
        
        # Prüfe Ergebnisse
        assert best_name is not None
        assert isinstance(best_name, str)
        assert isinstance(best_score, StrategyScore)
        assert best_score.score > 0
        assert best_score.total_trades >= 5
        
        # Prüfe dass Ergebnisse gespeichert wurden
        assert len(selector.results) > 0
        assert best_name in selector.results
    
    def test_run_selection_filters_insufficient_trades(self):
        """Test dass Strategien mit zu wenig Trades gefiltert werden"""
        # Generiere sehr kurze Daten
        data = generate_sample_data(n_bars=200, start_price=30000)
        
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=50  # Sehr hoch, sollte viele filtern
        )
        
        try:
            best_name, best_score = selector.run_selection(data)
            # Wenn es funktioniert, sollte mindestens eine Strategie gefunden werden
            assert best_name is not None
        except ValueError as e:
            # Erwarteter Fehler wenn keine Strategie genug Trades hat
            assert "Keine gültigen Strategien" in str(e)
    
    def test_export_ranking(self, tmp_path):
        """Test Export des Rankings als CSV"""
        # Erstelle Selector mit Test-Daten
        data = generate_sample_data(n_bars=500, start_price=30000)
        selector = StrategySelector(min_trades=5)
        
        # Führe Auswahl durch
        best_name, best_score = selector.run_selection(data)
        
        # Export
        export_file = tmp_path / "test_ranking.csv"
        selector.export_ranking(str(export_file))
        
        # Prüfe dass Datei existiert
        assert export_file.exists()
        
        # Lade und prüfe CSV
        df = pd.read_csv(export_file)
        assert len(df) > 0
        assert 'strategy_name' in df.columns
        assert 'score' in df.columns
        assert 'roi' in df.columns
        assert 'sharpe_ratio' in df.columns
    
    def test_strategy_score_dataclass(self):
        """Test StrategyScore Dataclass"""
        score = StrategyScore(
            name="Test Strategy",
            score=75.5,
            roi=25.0,
            sharpe_ratio=1.5,
            calmar_ratio=2.0,
            max_drawdown=-10.0,
            win_rate=60.0,
            total_trades=50,
            avg_trade=5.0,
            final_capital=12500.0,
            metrics={}
        )
        
        assert score.name == "Test Strategy"
        assert score.score == 75.5
        assert score.roi == 25.0
        assert score.total_trades == 50
    
    def test_weight_normalization(self):
        """Test dass Gewichte nicht mehr als 100% ergeben müssen"""
        # Gewichte müssen nicht auf 1.0 summieren
        custom_weights = {
            'roi': 0.4,
            'sharpe_ratio': 0.3,
            'calmar_ratio': 0.2,
            'win_rate': 0.1,
            'max_drawdown': 0.1
        }
        
        selector = StrategySelector(weights=custom_weights)
        
        # Score-Berechnung sollte trotzdem funktionieren
        metrics = {
            'roi': 20.0,
            'sharpe_ratio': 1.5,
            'calmar_ratio': 1.2,
            'win_rate': 60.0,
            'max_drawdown': -8.0
        }
        
        score = selector.calculate_score(metrics)
        assert 0 <= score <= 120  # Kann über 100 sein wegen Gewichtung


class TestIntegration:
    """Integrationstests für die gesamte Pipeline"""
    
    def test_full_workflow(self):
        """Test vollständiger Workflow von Daten bis Auswahl"""
        # 1. Generiere Daten
        data = generate_sample_data(n_bars=800, start_price=30000)
        assert len(data) == 800
        
        # 2. Erstelle Selector
        selector = StrategySelector(
            initial_capital=10000.0,
            trade_size=100.0,
            min_trades=5
        )
        
        # 3. Setup Strategien
        strategies = selector.setup_strategies()
        assert len(strategies) > 0
        
        # 4. Führe Auswahl durch
        best_name, best_score = selector.run_selection(data)
        
        # 5. Prüfe Ergebnisse
        assert best_name in strategies.keys()
        assert best_score.total_trades >= 5
        assert best_score.score > 0
        
        # 6. Prüfe dass beste Strategie tatsächlich höchsten Score hat
        for name, result in selector.results.items():
            if name != best_name:
                assert result.score <= best_score.score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
