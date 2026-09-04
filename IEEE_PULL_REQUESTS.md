# 🚀 IEEE Contributions - Pull Requests & Status Report

**Repository:** https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM  
**Contributor:** SriRamkunamsetty (IEEE Contributor)  
**Total Pull Requests:** 11  

---

### 1. PR #6
• 🔗 **Pull Request Number & Link:** #6 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/6  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-24 11:08:40 UTC (04:38:40 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #1 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/1)  
• 📝 **Short summary of the work done:**  
Hardened data cleaning pipeline to eliminate corrupted sentinel IDs (`-2147483648`), introduced `backend/data_utils.py` for working-directory-independent data loading and centralized product pricing formula `(ProdID % 2500) + 499`, and stabilized return types across collaborative, content-based, and rating-based recommendation algorithms to prevent runtime crashes.

---

### 2. PR #7
• 🔗 **Pull Request Number & Link:** #7 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/7  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-24 11:08:51 UTC (04:38:51 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #2 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/2)  
• 📝 **Short summary of the work done:**  
Isolated user identity by deterministically mapping Firebase UIDs to stable numeric IDs for recommendations, implemented wishlist synchronization per authenticated UID, ensured session cleanup on logout, and added an explicit removal action for wishlist cards.

---

### 3. PR #8
• 🔗 **Pull Request Number & Link:** #8 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/8  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-24 11:09:01 UTC (04:39:01 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #3 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/3)  
• 📝 **Short summary of the work done:**  
Enabled guest catalog browsing with cold-start fallbacks, implemented URL query encoding and literal substring matching to avoid regex syntax errors, added controlled 404/not-found states for invalid product routes, and corrected cart calculations using quantity-aware line totals.

---

### 4. PR #9
• 🔗 **Pull Request Number & Link:** #9 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/9  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-24 11:09:10 UTC (04:39:10 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #4 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/4)  
• 📝 **Short summary of the work done:**  
Added input validation for shipping details (name, valid phone number, address), established an end-to-end pending-to-paid order lifecycle with demo payment simulation, persisted user orders in Firebase, and created responsive empty and populated views in `/orders`.

---

### 5. PR #10
• 🔗 **Pull Request Number & Link:** #10 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/10  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-24 11:09:19 UTC (04:39:19 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #5 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/5)  
• 📝 **Short summary of the work done:**  
Grounded the Groq shopping assistant in the canonical catalog dataset and pricing utility to prevent hallucinations, added visible error handling when `GROQ_API_KEY` is missing, rewrote `README.md` with accurate Reflex startup instructions, and introduced the initial automated test suite in `tests/test_core_fixes.py`.

---

### 6. PR #12
• 🔗 **Pull Request Number & Link:** #12 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/12  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-27 16:55:41 UTC (10:25:41 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #11 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/11)  
• 📝 **Short summary of the work done:**  
Fixed a severe defect where user logout wiped persisted Firebase cart and wishlist data by introducing `clear_cart_locally()` and `clear_wishlist_locally()` for in-memory session cleanup only, preserving the user's saved items across logins.

---

### 7. PR #14
• 🔗 **Pull Request Number & Link:** #14 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/14  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-27 16:57:42 UTC (10:27:42 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #13 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/13)  
• 📝 **Short summary of the work done:**  
Imported and registered missing `ProductsState` and `PaymentState` classes in the secondary package entrypoint (`AI_Enabled_Recommendation_Engine_for_an_E_commerce_Platform.py`), ensuring parity with root `app.py` and preventing missing state runtime errors.

---

### 8. PR #16
• 🔗 **Pull Request Number & Link:** #16 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/16  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-27 17:01:08 UTC (10:31:08 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #15 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/15)  
• 📝 **Short summary of the work done:**  
Reset `ProductsState.search_query` prior to loading search history from Firebase, preventing query leakage when switching between accounts that lack previous search history.

---

### 9. PR #18
• 🔗 **Pull Request Number & Link:** #18 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/18  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-27 17:01:55 UTC (10:31:55 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #17 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/17)  
• 📝 **Short summary of the work done:**  
Made `canonical_products()` resilient against schema variants by providing fallback grouping when text columns are omitted and assigning default empty `ImageURL` and `NA` ratings when respective columns are absent.

---

### 10. PR #20
• 🔗 **Pull Request Number & Link:** #20 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/20  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-08-27 17:05:12 UTC (10:35:12 PM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #19 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/19)  
• 📝 **Short summary of the work done:**  
Added `scripts/quality_checks.sh` to execute unit tests, Python compilation, Pyflakes linting, and git whitespace checks sequentially with fail-fast validation.

---

### 11. PR #22
• 🔗 **Pull Request Number & Link:** #22 - https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/pull/22  
• 🟢 **Status:** OPEN  
• 📅 **Date & Time:** 2026-09-04 03:46:51 UTC (09:16:51 AM IST)  
• 🎯 **Issue Number Solved:** Fixes Issue #21 (https://github.com/SriRamkunamsetty/AI-RECOMMENDATION-ENGINE-FOR-AN-E-COMMERCE-PLATFORM/issues/21)  
• 📝 **Short summary of the work done:**  
Fixed cart subtotal `ValueError` crash when adding items priced >= ₹1,000 with comma formatting, added automatic cold-start fallback recommendations for authenticated users without interaction history, resolved column name collision (`Rating`) in rating-based recommendations, standardized pricing across recommenders using `data_utils.format_price()`, included product tags in catalog search filter, and added comprehensive unit test coverage.
