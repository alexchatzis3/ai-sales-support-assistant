# Test Cases

This document contains manual test cases used to validate the AI Sales & Support Assistant.

## 1. Product Recommendation Tests

### Test 1.1 — Gaming Laptop Recommendation

**User input:**

```text
Θέλω laptop για gaming μέχρι 900€
```

**Expected behavior:**
- Route should be `products`
- Assistant should recommend a gaming laptop
- Answer should mention product name and price
- Answer should explain why the product matches the use case


### Test 1.2 — Higher Budget Gaming Laptop

**User input:**

```text
Θέλω laptop για gaming μέχρι 1900€
```

**Expected behavior:**
- Route should be `products`
- Assistant should recommend suitable gaming laptops
- Answer should compare relevant options
- Answer should provide a final recommendation


### Test 1.3 — Monitor for Design

**User input:**

```text
Έχετε monitor για design;
```

**Expected behavior:**
- Route should be `products`
- Assistant should retrieve monitor-related products
- Answer should recommend a suitable desing/editing monitor


## 2. Store Policy Tests

### Test 2.1 — Return Policy

**User Input:**

```text
Ποια είναι η πολιτική επιστροφών;
```

**Expected behavior:**
- Route should be `policies`
- Assistant should answer using the return policy
- Answer should mention the 14-day return period


### Test 2.2 — Warranty Policy

**User Input:**

```text
Τι εγγύηση έχουν τα laptops;
```

**Expected behavior:**
- Route should be `policies`
- Assistant should explain the warranty duration
- Answer should be based on store policy context


### Test 2.3 — Box Now Shipping

**User Input:**

```text
Υποστηρίζετε Box Now;
```

**Expected behavior:**
- Route should be `policies`
- Assistant should answer using shipping policy context
- Answer should explain Box Now delivery availability


## 3. FAQ Tests

### Test 3.1 — Store Opening Hours

**User Input:**

```text
Ποιες είναι οι ώρες λειτουργίας;
```

**Expected behavior:**
- Route should be `faqs`
- Assistant should answer with store opening hours


### Test 3.2 — Store Pickup
**User Input:**

```text
Μπορώ να παραλάβω από το κατάστημα;
```

**Expected behavior:**
- Route should be `faqs`
- Assistant should explain store pickup availability


## 4. Conversation Memory Tests

### Test 4.1 — Remember Product Recommendation

**Conversation:**

```text
User: Θέλω laptop για gaming μέχρι 900€
Assistant: ...
User: Τι μου πρότεινες τελικά;
```

**Expected behavior:**
- Assistant should remember the previous recommendation
- Assistant should mention the previously recommended product


### Test 4.2 — Remember User Name

**Conversation:**

```text
User: Με λένε Αλέξανδρο
Assistant: ...
User: Πώς με λένε;
```

**Expected behavior:**
- Assistant should use conversation memory
- Assistant should answer that the user's name is Αλέξανδρος


### Test 4.3 — Remember Budget

**Conversation:**

```text
User: Θέλω laptop
Assistant: ...
User: Μέχρι 900€
Assistant: ...
User: Για gaming
```

**Expected behavior:**
- Assistant should combine previous context
- Assistant should understand that the user wants a gaming laptop up to 900€


## 5. Out-of-Scope Tests

### Test 5.1 — Unrelated Question

**User input:**

```text
Πες μου την ιστορία της Ρώμης.
```

**Expected behavior:**
- Assistant should not answer as a general-purpose chatbot
- Assistant should politely redirect the user to store-related help