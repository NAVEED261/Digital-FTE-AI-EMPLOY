# Dictionary Optimization for Court Reporting

A well-optimized dictionary is the foundation of fast, accurate court reporting. This guide covers maintenance, conflict resolution, and speed optimization.

## Dictionary Maintenance Schedule

### Daily (During Practice/Court)

- **Note words that cause problems**: Keep list of words that stall or cause errors
- **Document unfamiliar terms**: Legal terms you encounter for the first time
- **Check for conflicts**: Words that produce wrong output

### Weekly

- **Add new terms**: Add 10-20 new legal terms discovered
- **Fix errors**: Correct entries that caused mistakes
- **Review error log**: Analyze what went wrong and why
- **Backup dictionary**: Save current version

### Monthly

- **Full dictionary audit**: Check for duplicate entries
- **Conflict analysis**: Run Plover's conflict checker
- **Speed analysis**: Identify where you're slow
- **Reorganize entries**: Clean up unused briefs

### Quarterly

- **Dictionary rebuild**: Reorganize for efficiency
- **Benchmark speed**: Measure WPM improvement
- **Specialize by case**: Add terms for upcoming cases
- **Archive old entries**: Move rarely-used terms to archive

## Handling Dictionary Conflicts

### What is a Conflict?

When two different words map to the same chord:

```json
{
  "KO RT": "court",        // Conflict!
  "KO RT": "caught"        // Same chord, different word
}
```

Plover chooses based on priority order.

### Finding Conflicts

**In Plover:**
1. Tools > Check Dictionaries > Check for conflicts
2. View conflict report
3. Note conflicting words

**Manually:**
Use a JSON viewer or text editor to search for duplicate keys.

### Resolving Conflicts

**Option 1: Reassign One Chord**

```json
// Original (conflict):
"KO RT": "court",
"KO RT": "caught"

// Solution:
"KO RT": "court",        // Keep common word
"KAU T": "caught"        // Assign different chord
```

**Option 2: Use Context Rules**

Plover's orthography system can handle some conflicts:

```json
// Rule: context determines word
"{}": "court",           // Default
"caught {}" : "caught"   // When followed by specific word
```

**Option 3: Create Multi-Stroke Entry**

```json
// Split into multiple strokes:
"CAUGHT": "cau",
"KO RT": "court",        // Now no conflict
"CAUGHT T": "caught"     // Multi-stroke for catch
```

**Option 4: Use Different Dictionary Layer**

- Put court-specific words in legal dictionary (high priority)
- Keep general words in main dictionary (low priority)
- Plover uses highest priority match

## Speed Optimization Techniques

### 1. Reduce Dictionary Size

**Why**: Smaller dictionaries = faster lookup = faster output

**How:**
- Remove rarely-used entries
- Archive specialty terms (medical, technical)
- Keep only active, frequently-used words
- Target: 50-80k entries (optimal range)

### 2. Create Efficient Briefs

**Short briefs for common words:**

```json
// Good briefs (fast):
"TH": "the",             // 1 stroke
"TORN": "attorney",      // 1 stroke
"KASE": "case",          // 1 stroke

// Poor briefs (slower):
"THEE": "the",           // Extra stroke
"THORN E": "attorney",   // 2 strokes
"KAYS": "case",          // Extra strokes
```

**Principle**: 1 stroke = fastest, 2 strokes = acceptable, 3+ strokes = slow

### 3. Organize Dictionary Logically

Group similar terms:

```json
// Court procedures (section 1)
"KO RT": "court",
"JUJ": "judge",
"WIT NS": "witness",

// Legal terms (section 2)
"THORN E": "attorney",
"PLANT F": "plaintiff",
"DEF DANT": "defendant",

// Common phrases (section 3)
"FOR REC": "for the record",
"YOUR HON": "your honor"
```

### 4. Use Phrase Briefs for Common Sequences

Instead of writing each word separately:

```json
// Without briefs (3 strokes):
"TH": "the"
"KASE": "case"
"S": "is"
// Typing: TH KASE S (3 strokes)

// With phrase brief (1 stroke):
"THKAYS": "the case is"
// Typing: THKAYS (1 stroke - much faster!)
```

### 5. Optimize Suffix Handling

Use Plover's suffix system:

```json
// Base word:
"TEST": "test",

// Automatic suffixes (Orthography rules):
"TEST + ING" = "testing"     // Suffix rule adds -ing
"TEST + ED" = "tested"       // Suffix rule adds -ed
"TEST + S" = "tests"         // Suffix rule adds -s

// No need for separate entries!
```

### 6. Dictionary Categorization

**Active Dictionary (50-80k entries):**
- Common English words
- All legal terminology
- Frequently-used briefs
- Specialized terms for current cases

**Archive Dictionary (load as needed):**
- Medical terminology
- Technical terms
- Rare/specialty briefs
- Client-specific terms

**Reference Dictionary (never load):**
- Old/deprecated entries
- Personal practice briefs
- Historical dictionary versions

## Conflict Resolution Workflow

### Step 1: Identify the Conflict
```
Plover reports: "KO RT" has 2 definitions
- "court" (in main dictionary)
- "caught" (in personal dictionary)
```

### Step 2: Determine Priority
```
Which word is more important for court reporting?
- "court" = CRITICAL (appear 100+ times per case)
- "caught" = RARE (appears maybe 2-3 times)
```

### Step 3: Keep High-Priority Word
```
Keep: "KO RT" = "court"
```

### Step 4: Reassign Low-Priority Word
```
Find alternate chord for "caught":
"KAU T" = "caught"  // New chord
```

### Step 5: Test Thoroughly
```
1. Remove old entry from dictionary
2. Add new entry
3. Restart Plover
4. Test with sample text
5. Verify correct output
```

## Building Efficient Phrase Briefs

### Identify Phrases to Brief

Look for phrases that appear frequently:

```
High-frequency phrases:
1. "your honor"
2. "for the record"
3. "let the record show"
4. "if you recall"
5. "do you remember"
6. "is that correct"
7. "and what is"
8. "at that time"
```

### Create Brief Chords

```json
// Phrase briefs (one chord per phrase):
"YOUR HON": "your honor",
"FOR REC": "for the record",
"LET REC SHOW": "let the record show",
"IF KALE": "if you recall",
"DO REM": "do you remember",
"KOREKT": "is that correct",
"AND WHAT S": "and what is",
"AT THAT T": "at that time"
```

### Measure Impact

Count occurrences in sample text:
- "your honor" appears 47 times per 100-page transcript
- One brief saves 47 extra strokes = **huge speed increase**

### Create Case-Specific Phrases

For upcoming cases, pre-create briefs:

```json
// For witness "John Smith":
"JOHN": "john smith",

// For company "Acme Corporation":
"ACME": "acme corporation",

// For repeated legal phrase in case:
"BREACH": "breach of contract",
"LIA BIL": "liability",
```

## Speed Measurement & Benchmarking

### Before Optimization
1. Take speed test (baseline): 120 WPM
2. Record accuracy: 95%
3. Note problem areas: Numbers, medical terms, names

### After Optimization
1. Add briefs for problem words
2. Remove conflicts
3. Test again: 130 WPM
4. Compare improvement: +10 WPM = 8% faster

### Ongoing Optimization

Track improvements over time:

```
Week 1: 100 WPM, 90% accuracy
Week 2: 105 WPM, 92% accuracy (+5 WPM, +2%)
Week 3: 110 WPM, 94% accuracy (+5 WPM, +2%)
Month 1: 125 WPM, 97% accuracy (+25 WPM, +7%)
```

## Dictionary Backup & Version Control

### Backup Strategy

Save copies at different stages:

```
dictionary-v1.0.json    (baseline)
dictionary-v1.1.json    (after legal terms added)
dictionary-v1.2.json    (after speed optimization)
dictionary-v1.3.json    (after conflict resolution)
```

### Backup Locations

1. **Local backup**: Save copy on computer
2. **Cloud backup**: Upload to cloud storage (OneDrive, Google Drive)
3. **External drive**: Copy to USB flash drive
4. **Version control**: Use Git for tracking changes

### Restore from Backup

If dictionary gets corrupted or entries are accidentally deleted:

1. Locate backup file
2. In Plover: Settings > Dictionaries
3. Remove corrupted dictionary
4. Add backup dictionary
5. Restart Plover
6. Verify all entries present

## Common Optimization Mistakes to Avoid

### ❌ Don't: Create overly-complex briefs
```json
// Too complex:
"STPK W H AE O U F R P B L G T S D Z": "this case"
```

### ✅ Do: Keep briefs simple
```json
// Simple and efficient:
"THIS KASE": "this case"
```

### ❌ Don't: Create conflicting briefs
```json
// Conflict:
"KO RT": "court"
"KO RT": "caught"
```

### ✅ Do: Resolve conflicts immediately
```json
// No conflict:
"KO RT": "court"
"KAU T": "caught"
```

### ❌ Don't: Keep unused entries
```json
// Takes up space, slows lookup:
"OLD PHRASE": "phrase never used"
```

### ✅ Do: Archive unused entries
Move to separate dictionary, load only if needed.

### ❌ Don't: Optimize prematurely
Focus on accuracy first, then speed.

### ✅ Do: Build speed gradually
1. Get accurate at 80 WPM
2. Improve briefs for speed
3. Target 100 WPM
4. Continue optimization to 150, 200+ WPM

## Professional Tips

1. **Share dictionaries**: Exchange with other court reporters
2. **Review famous reporters' briefs**: Learn from experts
3. **Specialize by field**: Create dictionaries for specific legal domains
4. **Keep improvement log**: Track progress over months/years
5. **Join communities**: Learn optimization tips from peers

---

**Golden Rule**: A optimized dictionary is the difference between 100 WPM and 200 WPM. Invest in maintenance and optimization throughout your career.
