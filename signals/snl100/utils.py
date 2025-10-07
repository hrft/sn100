def validate_df(df, min_rows=60):
    """
    بررسی اولیه سلامت داده برای تحلیل سیگنال:
    - تعداد کندل کافی باشه
    - ستون‌های مورد نیاز وجود داشته باشن
    - هیچ‌کدوم از ستون‌ها تهی یا صفر نباشن
    """
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        return False, f"❌ ستون‌های ناقص: {missing}"

    if len(df) < min_rows:
        return False, f"❌ تعداد کندل ناکافی: فقط {len(df)} ردیف"

    for col in required_cols:
        if df[col].isnull().any():
            return False, f"❌ داده تهی در ستون {col}"
        if df[col].sum() == 0:
            return False, f"❌ مجموع صفر در ستون {col}"

    return True, "✅ داده سالم و قابل تحلیل"

