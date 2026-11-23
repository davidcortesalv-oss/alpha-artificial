"""Proves aïllades: ni APIs ni historial real ni rondes d'inversió."""
import csv
import importlib.util
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
fake_config = types.SimpleNamespace(CARPETA_DADES="dades")
fake_torneo = types.SimpleNamespace()
spec = importlib.util.spec_from_file_location("prices_under_test", ROOT / "actualitzar_preus.py")
prices = importlib.util.module_from_spec(spec)
with patch.dict("sys.modules", {"config": fake_config, "torneo": fake_torneo}):
    spec.loader.exec_module(prices)


class DailyPricesTests(unittest.TestCase):
    def setUp(self):
        (ROOT / "output").mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(dir=ROOT / "output", prefix="prova-preus-")
        self.addCleanup(self.folder.cleanup)
        self.csv = str(Path(self.folder.name) / "valors.csv")

    def rows(self):
        with open(self.csv, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def test_refresh_same_day_replaces_provisional_prices(self):
        prices.guardar_valors(self.csv, "2026-11-20", {"gpt": 100, "index": 101})
        original = self.rows()
        prices.guardar_valors(self.csv, "2026-11-23", {"gpt": 98, "index": 99})
        self.assertEqual(prices.guardar_valors(self.csv, "2026-11-23", {"gpt": 96, "index": 97}), 2)
        rows = self.rows()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[:2], original)
        self.assertEqual([float(r["valor"]) for r in rows[2:]], [96, 97])

    def test_identical_prices_are_idempotent(self):
        prices.guardar_valors(self.csv, "2026-11-23", {"gpt": 99.123})
        before = Path(self.csv).read_bytes()
        self.assertEqual(prices.guardar_valors(self.csv, "2026-11-23", {"gpt": 99.124}), 0)
        self.assertEqual(Path(self.csv).read_bytes(), before)

    def test_stale_or_invalid_values_never_change_file(self):
        prices.guardar_valors(self.csv, "2026-11-23", {"gpt": 100})
        before = Path(self.csv).read_bytes()
        for day, values in [("2026-11-20", {"gpt": 90}), ("2026-11-23", {"gpt": float("nan")}),
                            ("2026-11-23", {"gpt": 0})]:
            with self.assertRaises(ValueError):
                prices.guardar_valors(self.csv, day, values)
            self.assertEqual(Path(self.csv).read_bytes(), before)

    def test_missing_held_asset_does_not_create_a_valuation(self):
        fake_torneo.carregar_estat = lambda: {"carteres": {"gpt": {"NVDA": 1}}, "index_unitats": 1}
        fake_torneo.baixar_preus = lambda: {"SPY": 100}
        fake_torneo.ULTIMA_DATA_MERCAT = "2026-11-23"
        with patch.object(prices, "RUTA_DIARIS", self.csv), self.assertRaisesRegex(ValueError, "NVDA"):
            prices.main()
        self.assertFalse(Path(self.csv).exists())

    def test_empty_market_date_does_not_invent_today(self):
        fake_torneo.carregar_estat = lambda: {"carteres": {"gpt": {"NVDA": 1}}}
        fake_torneo.baixar_preus = lambda: {"SPY": 100, "NVDA": 10}
        fake_torneo.ULTIMA_DATA_MERCAT = None
        with patch.object(prices, "RUTA_DIARIS", self.csv), self.assertRaises(ValueError):
            prices.main()
        self.assertFalse(Path(self.csv).exists())


if __name__ == "__main__":
    unittest.main()
