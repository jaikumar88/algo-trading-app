from telegram_bot import analyze_trade_text


def test_simple_buy():
    txt = "BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000"
    out = analyze_trade_text(txt)
    assert "Intent: BUY" in out
    assert "Symbol: BTC/USDT" in out or "Symbol: BTC" in out
    assert "Price: 30000" in out


def test_messy_ocr():
    txt = "Crypto Trading with PRT\n...\nEETHLS\nEoll Brackel Ordar Etusd\nEntv Prico 417]"
    out = analyze_trade_text(txt)
    # Analyzer may return either a short extracted-text snippet or a detected-trade summary
    assert out.startswith("Extracted text") or out.startswith("Detected trade") or "Intent:" in out
