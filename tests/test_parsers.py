"""Tests for Visa and Max parsers."""

from pathlib import Path

import pytest

from myfinance.parsers.visa import VisaParser
from myfinance.parsers.max_parser import MaxParser


class TestVisaParser:
    def setup_method(self):
        self.parser = VisaParser(source_label='visa-mizrahi')

    def test_parse_sample_csv(self, sample_data_dir):
        txns = self.parser.parse(sample_data_dir / "visa_sample.csv")
        assert len(txns) == 11
        assert txns[0]['merchant'] == 'שופרסל דיל 1234'
        assert txns[0]['date'] == '2026-03-05'
        assert txns[0]['amount_ils'] == 350.00
        assert txns[0]['source'] == 'visa-mizrahi'

    def test_parse_installments(self, sample_data_dir):
        txns = self.parser.parse(sample_data_dir / "visa_sample.csv")
        installment_txn = [t for t in txns if t['installment_number'] is not None]
        assert len(installment_txn) == 1
        assert installment_txn[0]['installment_number'] == 3
        assert installment_txn[0]['installments_total'] == 12

    def test_parse_foreign_currency(self, sample_data_dir):
        txns = self.parser.parse(sample_data_dir / "visa_sample.csv")
        usd_txns = [t for t in txns if t['currency_original'] == 'USD']
        assert len(usd_txns) == 1
        assert usd_txns[0]['amount_original'] == 29.99

    def test_diners_uses_same_parser(self, sample_data_dir):
        diners_parser = VisaParser(source_label='diners-el-al')
        txns = diners_parser.parse(sample_data_dir / "visa_sample.csv")
        assert all(t['source'] == 'diners-el-al' for t in txns)

    def test_empty_dates_skipped(self):
        import tempfile
        csv_content = "תאריך עסקה,שם בית העסק,סכום חיוב\n,,100\n05/03/2026,test,50\n"
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', encoding='utf-8', delete=False) as f:
            f.write(csv_content)
            f.flush()
            txns = self.parser.parse(Path(f.name))
        assert len(txns) == 1


class TestMaxParser:
    def setup_method(self):
        self.parser = MaxParser()

    def test_parse_sample_csv(self, sample_data_dir):
        txns = self.parser.parse(sample_data_dir / "max_sample.csv")
        assert len(txns) == 10
        assert txns[0]['merchant'] == 'קסטרו'
        assert txns[0]['source'] == 'max'

    def test_parse_foreign_currency(self, sample_data_dir):
        txns = self.parser.parse(sample_data_dir / "max_sample.csv")
        usd_txns = [t for t in txns if t['currency_original'] == 'USD']
        assert len(usd_txns) == 1
        assert usd_txns[0]['merchant'] == 'NETFLIX.COM'
