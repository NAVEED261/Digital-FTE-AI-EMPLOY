# Legal Dictionary Guide for Court Stenography

Building and maintaining a legal dictionary is critical for court reporting speed and accuracy.

## Dictionary Structure

A steno dictionary is a JSON file mapping chords to words/phrases:

```json
{
  "KO RT": "court",
  "JUJ": "judge",
  "WIT NS": "witness",
  "THORN E": "attorney",
  "KASE": "case",
  "TRAUL": "trial",
  "TEST MON E": "testimony",
  "PLANT F": "plaintiff",
  "DEF DANT": "defendant"
}
```

**Dictionary types:**
1. **Main dictionary**: Core vocabulary (50k+ entries)
2. **Legal dictionary**: Court-specific terms
3. **Personal dictionary**: Custom briefs (your unique additions)
4. **Client dictionary**: Case-specific terminology

## Essential Legal Terms for Court

### Court Procedures

| Term | Chord | Notes |
|------|-------|-------|
| COURT | KO RT | Primary location |
| JUDGE | JUJ | Decision maker |
| JURY | JUR E | Fact finders |
| WITNESS | WIT NS | Testimony provider |
| ATTORNEY | THORN E | Legal representative |
| COUNSEL | KOW NS L | Lawyer (alternate) |
| PLAINTIFF | PLANT F | Suing party |
| DEFENDANT | DEF DANT | Sued/accused party |
| PROSECUTION | PROS KUTE | Criminal case prosecutor |
| DEFENSE | DEF NS | Defendant's side |

### Trial Procedures

| Term | Chord | Notes |
|------|-------|-------|
| TESTIMONY | TEST MON E | Witness statement |
| EVIDENCE | EVD NS | Proof presented |
| OBJECTION | OBJ K SH UN | Attorney challenge |
| SUSTAIN | SUS TANE | Judge agrees (upholds) |
| OVERRULE | O VER RULE | Judge disagrees (rejects) |
| ADMISSIBLE | AD MIS BL | Allowed as evidence |
| HEARSAY | HEAR SA E | Testimony issue |
| CROSS-EXAMINE | KROS ZAM | Challenge witness |
| DIRECT EXAMINATION | DER EKT ZAM | Initial questioning |
| REDIRECT | RE DER EKT | Follow-up questioning |

### Legal Document Types

| Document | Chord | Notes |
|----------|-------|-------|
| COMPLAINT | KOPLAINT | Initial lawsuit document |
| DEPOSITION | DEP SITION | Out-of-court testimony |
| AFFIDAVIT | AF AV IT | Sworn statement |
| MOTION | MOE SHEN | Request to court |
| BRIEF | BREF | Legal argument document |
| CONTRACT | KONT RACT | Agreement |
| DEED | DEED | Property transfer |
| STATUTE | STAT UT | Law |
| ORDINANCE | OR DIN ANS | Local law |
| JUDGMENT | JUJ MENT | Court decision |

### Criminal Law Terms

| Term | Chord | Notes |
|------|-------|-------|
| GUILTY | GIL TE | Verdict |
| INNOCENT | IN O SENT | Verdict |
| ACQUIT | AK WIT | Release verdict |
| CONVICT | KONVIK | Guilty verdict |
| FELONY | FEL O NE | Serious crime |
| MISDEMEANOR | MIS DE MEAN OR | Lesser crime |
| ARRAIGN | AE RAIN | Bring to court |
| PLEAD | PLEED | Make statement |
| BAIL | BALE | Release condition |
| PAROLE | PAE ROLE | Early release |

### Civil Law Terms

| Term | Chord | Notes |
|------|-------|-------|
| NEGLIGENCE | NEG L JENS | Failure to care |
| DAMAGES | DAM AJ | Compensation |
| LIABILITY | LI A BIL I TE | Responsibility |
| CONTRACT | KONT RACT | Agreement |
| BREACH | BREECH | Violation |
| TORT | TORT | Wrongful act |
| SETTLEMENT | SET L MENT | Agreement to end |
| MEDIATION | MED E AE SH UN | Dispute resolution |
| ARBITRATION | AR BIT RAE SH UN | Dispute resolution |
| INJUNCTION | IN JUNK SH UN | Court order to stop |

### Procedural Language

| Phrase | Chord | Notes |
|--------|-------|-------|
| FOR THE RECORD | FOR REC | Formal statement |
| LET THE RECORD SHOW | LET REC SHOW | Formal statement |
| MAY IT PLEASE THE COURT | MAE PLOOZ KO RT | Opening phrase |
| YOUR HONOR | YOUR HON | Judge address |
| STIPULATION | STIP U LAE SH UN | Agreed fact |
| FOUNDATION | FOUN DAE SH UN | Evidence requirement |
| RELEVANCE | REL E VANS | Connection to case |
| PREJUDICIAL | PREJ U DISH L | Unfairly damaging |

## Building Your Dictionary

### Phase 1: Start with Foundation
1. Load Plover's default dictionary (50k+ entries)
2. Add a legal term package (NCRA-standard dictionary)
3. Test with sample court transcripts

### Phase 2: Customize for Your Style
1. **Identify your frequent errors**: What words do you struggle with?
2. **Add personal briefs**: Create shortcuts for words you type often
3. **Test thoroughly**: Practice before court use
4. **Document conflicts**: Note when briefs create ambiguity

### Phase 3: Specialize by Case Type
1. **Criminal law**: Add crime, evidence, procedure terms
2. **Civil law**: Add damages, contract, liability terms
3. **Family law**: Add custody, support, dissolution terms
4. **IP law**: Add patent, trademark, copyright terms

## Dictionary Entry Examples

### Single Word Entries
```json
{
  "KO RT": "court",
  "JUJ": "judge",
  "LAW": "law"
}
```

### Multi-Word Phrase Briefs
```json
{
  "FPLAEZ": "for the record",
  "YOUR HON": "your honor",
  "MAE PLOOZ": "may it please"
}
```

### Disambiguation (Homophones)
```json
{
  "TO": "to",
  "TOO": "too",
  "TWO": "two"
}
```

In Plover, you handle these with unique chords or context-based definitions.

## Dictionary Maintenance

### Regular Tasks
- **Weekly**: Add new terms encountered in court
- **Monthly**: Review error logs and fix conflicts
- **Quarterly**: Clean up unused or incorrect entries
- **Annually**: Rebuild dictionary for organization

### Handling Conflicts
When two different words map to the same chord:

1. **Check Plover's conflict list** in software
2. **Reassign one chord** - Use alternate stroking
3. **Add context rule** - Use Plover's orthography settings
4. **Use longer strokes** - Split into multiple chords

Example:
```json
"COURT": "court",     // Keeps common version
"KO URTD": "courted"  // Adds "D" to distinguish
```

### Performance Optimization

**Dictionary size matters:**
- 50k entries: Standard, good performance
- 100k entries: Comprehensive, slower lookup
- 200k+ entries: Specialty, significant lag

**Best practice:**
- Keep 50-80k entries in active dictionary
- Archive old/unused entries
- Maintain separate specialty dictionaries (load as needed)

## Common Briefs for Speed

### Articles & Prepositions
```
"TH": "the"
"AND": "and"
"AT": "at"
"OR": "or"
"IN": "in"
"OF": "of"
"FOR": "for"
```

### Common Verbs
```
"S": "is"
"WAS": "was"
"WILL": "will"
"CAN": "can"
"HAS": "has"
"HAVE": "have"
```

### Question Words
```
"WHAT": "what"
"WHO": "who"
"WHERE": "where"
"WHEN": "when"
"WHY": "why"
"HOW": "how"
```

## Legal-Specific Briefs

Create your own briefs for commonly spoken phrases in courtrooms:

```json
{
  "OBJ": "objection",
  "SUST": "sustain",
  "OVERRUL": "overrule",
  "STIPUL": "stipulation",
  "DIRECT": "direct examination",
  "CROSS": "cross-examination",
  "FOUNDATION": "foundation",
  "RELEVANCE": "relevance"
}
```

## Tips for Dictionary Building

1. **Start general, then specialize** - Use default dictionary first
2. **Add incrementally** - Don't try to add 1000 words at once
3. **Test before court** - Verify new entries work correctly
4. **Document everything** - Keep notes on custom briefs
5. **Back up regularly** - Save dictionary copies frequently
6. **Review conflicts** - Check Plover's conflict reports monthly
7. **Share with peers** - Exchange dictionaries with other reporters

## Using Multiple Dictionaries

Plover supports layered dictionaries:

1. **System dictionary** (read-only): Default entries
2. **Main dictionary** (editable): Your customizations
3. **Personal dictionary** (editable): Custom briefs
4. **Professional dictionary** (case-specific): Specialty terms

Load in order of priority - newer entries override older ones.

## Resources

- **NCRA (National Court Reporters Association)**: Official dictionary standards
- **Plover Community**: Shared dictionaries and briefs
- **Open Steno Project**: Free dictionary resources
- **Legal lexicons**: Specialized legal terminology references

---

**Key Point**: Your dictionary is your competitive advantage. Invest time in building, testing, and maintaining it throughout your career.
