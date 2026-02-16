# Plover Setup Guide for Court Reporting

Plover is the most widely used open-source steno software. This guide covers setup and configuration for court reporting.

## Installation

### Windows
1. Download from [plover.readthedocs.io](https://plover.readthedocs.io)
2. Run the installer
3. Choose installation directory (recommend C:\Plover)
4. Complete setup

### Mac
1. Download DMG file
2. Drag Plover to Applications folder
3. Launch from Applications

### Linux
1. Install via package manager or download AppImage
2. Make executable: `chmod +x plover-*.AppImage`
3. Run: `./plover-*.AppImage`

## Initial Configuration

### Machine Type Selection

Open **Settings > Machine**

**Options:**
- **Gemini PR**: Most common protocol (supports most machines)
- **Stentura**: For Stentura machines
- **TX Bolt**: For older TX Bolt machines
- **Keyboard**: Use computer keyboard (testing only)

**Recommendation**: Select based on your steno machine - check machine manual.

### Port Configuration

1. Go to **Settings > Machine**
2. Select **Port** - depends on machine:
   - USB: Select COM port (Windows) or /dev/ttyUSB (Linux)
   - Serial: Select serial port
   - Network: Enter IP address

**Troubleshooting connection:**
- Restart Plover
- Unplug/replug machine
- Check machine drivers installed
- Try different USB ports
- Check Device Manager (Windows) for port assignment

### Dictionary Setup

1. Open **Settings > Dictionaries**
2. Default dictionary loads automatically
3. **Add legal dictionary**:
   - Click "+" button
   - Browse to legal dictionary file
   - Add in order of priority (legal dict above default)

**Dictionary Order Matters:**
- Higher dictionaries override lower ones
- Personal dictionary should be last (highest priority)

## Plover Plugins for Court Reporting

Plugins extend Plover functionality. Install via **Tools > Plugin Manager**.

### Recommended Plugins

1. **Plover CAT** (Computer-Aided Transcription)
   - Creates formatted transcripts
   - Real-time translation output
   - Speaker management
   - Q&A formatting
   - Essential for court reporting

2. **Plover Stroke Lexicon**
   - Tracks which strokes produce which words
   - Helps analyze speed and patterns
   - Useful for practice and optimization

3. **Plover Rant** (Remote Access Notation Translator)
   - Allows remote machine access
   - Send translations remotely
   - Useful for distributed reporting

4. **Plover Text Prettify**
   - Auto-formats court language
   - Capitalizes proper nouns
   - Formats numbers and currency
   - Improves transcript quality

5. **Plover Suggestions**
   - Suggests dictionary entries while typing
   - Helps learn new briefs
   - Improves training speed

## Orthography Settings

Orthography rules handle automatic formatting.

**Access**: Settings > Orthography

### Common Court Reporting Rules

```
"{}{}{}{}": "{word}",           // Basic word
"{}~|": "{word}",                // Paragraph breaks
"{}-|": "{word}",                // Sentence breaks
"{}ing": "{word}ing",            // Add -ing suffix
"{}ed": "{word}ed",              // Add -ed suffix
"{}s": "{word}s",                // Pluralize
"{}tion": "{word}tion",          // Add -tion suffix
```

### Custom Rules for Court

```
// Capitalize at sentence start
"{^}{...}{-|}{WORD}": "{WORD}",

// Format numbers
"NUMB": "{0}",  // Number suffix

// Format currency
"DOLL": "$",
```

## Dictionaries: Which to Load?

### Essential Dictionaries for Court

1. **Plover Main Dictionary** (default)
   - 50,000+ general English words
   - Always load (core)

2. **Legal Dictionary** (NCRA-standard)
   - Court-specific terms
   - Load second priority

3. **Personal Dictionary** (your custom briefs)
   - Your unique additions
   - Load highest priority (overrides others)

4. **Specialty Dictionary** (case-specific)
   - Load only for specific cases
   - Medical, technical terms, proper names

### Dictionary Priority Order

```
1. Personal Dictionary (highest priority - loaded last)
2. Legal Dictionary
3. Default Plover Dictionary (lowest priority)
```

In Plover settings, order from top (least priority) to bottom (most priority).

## Real-Time Translation Setup

### For CAT Software Integration

1. **Plover CAT Plugin** (recommended)
   - Built-in real-time translation
   - Integrates with Plover directly
   - Outputs formatted transcript

2. **Export to File**
   - Configure output path: Settings > Output > Files
   - Specify transcript format (.rtf, .txt)
   - Real-time file updates

3. **Network Output** (Advanced)
   - Configure TCP/UDP output
   - Send to remote CAT software
   - Useful for distributed reporting

### Speaker Tagging (Plover CAT)

```
[SPEAKER:JUDGE]
Q: What is your name?
A: [SPEAKER:WITNESS]
My name is John Smith.
```

Configure speakers in CAT plugin settings:
- Judge
- Attorney (multiple)
- Witness
- Court Reporter
- Bailiff

## Speed Testing in Plover

### Built-in Speed Test

1. Go to **Tools > Speed Test**
2. Select difficulty level:
   - Easy (50 WPM target)
   - Medium (100 WPM target)
   - Hard (150 WPM target)
   - Expert (200+ WPM target)

3. Practice and receive feedback
4. Results save to history

### Custom Practice Material

Create custom dictation:
1. Tools > Create Dictation
2. Paste court transcript text
3. Set duration and difficulty
4. Practice against real material

## Sound & Feedback Configuration

### Audio Settings

1. **Settings > Audio**
2. **Enable sounds**:
   - Key clicks (feedback)
   - Error sounds (stroke mistakes)
   - Start/stop alerts

### Steno Sounds

- **Beep**: Audible feedback for each stroke
- **Higher pitch**: Error or conflict
- **Lower pitch**: Successful stroke

**Recommendation**: Enable for learning, disable during court.

## Export and Backup

### Saving Transcripts

1. **File > Export Transcript**
2. Choose format:
   - RTF (Rich Text Format) - preserves formatting
   - TXT (Plain text) - simple format
   - PDF (Professional documents)
   - DOCX (Word format)

### Backup Dictionary

1. **Tools > Backup**
2. Choose directory for backup
3. Saves all dictionaries and settings
4. Run weekly

### Restore from Backup

1. **Tools > Restore**
2. Select backup directory
3. Restores all settings and dictionaries

## Troubleshooting Common Issues

### Strokes Not Registering

**Problem**: Machine connected but no strokes appearing

**Solutions:**
1. Check machine connection (USB, serial)
2. Verify correct machine type selected
3. Test with keyboard machine type (if available)
4. Restart Plover
5. Check machine firmware

### Dictionary Conflicts

**Problem**: Wrong word appearing after stroke

**Solutions:**
1. Check dictionary order (personal dict highest)
2. Review conflicting entries
3. Use Plover's conflict report (Tools > Check Dictionaries)
4. Remove or reassign conflicting entry
5. Test change before court

### Performance Issues (Slow Response)

**Problem**: Lag between stroke and output

**Solutions:**
1. Reduce dictionary size (remove unused entries)
2. Disable unnecessary plugins
3. Update Plover to latest version
4. Close other applications
5. Increase Plover priority in Task Manager (Windows)

### Output Not Appearing

**Problem**: Strokes working but text not appearing

**Solutions:**
1. Check output method (clipboard, keyboard, file)
2. Verify focus is in correct application
3. Enable Plover's output in notifications
4. Check CAT software configuration
5. Test with Plover's transcript viewer

## Best Practices for Court

### Pre-Court Checklist

- [ ] Machine connected and tested (5 minutes before)
- [ ] Dictionary loaded and backed up
- [ ] Sound feedback disabled
- [ ] Output format verified
- [ ] CAT software running (if applicable)
- [ ] Transcript file saving properly
- [ ] Battery checked (if wireless machine)

### During Court

- Keep Plover running in background
- Monitor transcript as you write
- Note any words Plover struggles with
- Add corrections to dictionary after session

### Post-Court

1. Export final transcript
2. Review and correct if needed
3. Add new terms to dictionary
4. Back up dictionary
5. Clean up any temporary files

## Advanced: Custom Plugins

For advanced users, Plover supports custom Python plugins:

1. **Plugin API**: Available in Plover documentation
2. **Examples**: Check Plover community plugins on GitHub
3. **Development**: Requires Python knowledge

## Resources

- **Official Plover Docs**: plover.readthedocs.io
- **Community Forum**: Discord/Reddit Steno communities
- **Plugin Repository**: GitHub - openstenoproject
- **CAT Software**: Discuss options with other reporters

---

**Key Point**: Plover configuration is crucial for court reporting success. Take time to set it up correctly before your first court appearance.
