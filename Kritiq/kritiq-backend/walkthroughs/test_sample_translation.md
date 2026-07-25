# Walkthrough — Code Translation: `test_sample.py`

Translated `test_sample.py` from python to java.

## 📋 Overview

| | |
|---|---|
| **Source File** | `test_sample.py` |
| **From** | python |
| **To** | java |
| **Translated On** | 2026-07-13 17:23:57 |

## 💻 Translated Code

```java
public class DiscountCalculator {
    public static double calculateDiscount(double price, double discountPercent) {
        String unusedVar = "debug";
        double discountAmount = price * discountPercent / 100;
        double discounted = price - discountAmount;
        return discounted;
    }
}
```

## ✅ Recommended Next Steps
- [ ] Verify the translated code syntax and logic in the target environment.
- [ ] Compile or run tests to ensure behavioral equivalence with the original source code.

---
*Generated automatically by Kritiq's AI Translation Agent — 2026-07-13 17:23:57*
