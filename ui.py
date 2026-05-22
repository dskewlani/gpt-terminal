"""
ui.py — ProTrader Terminal v4 UI
Exact Upstox color schema from screenshots:
  - Background: #F7F8FA (page), #FFFFFF (cards)
  - Primary CTA purple: #5B2ECC  (deep Upstox violet)
  - Hover purple: #4F1DB5
  - Nav dark purple: #2D1066
  - Green (profit): #00B386
  - Red (loss):     #F45B69
  - Text: #1A1A2E  /  #4A4A6A  /  #7A7A9A
Fonts: Plus Jakarta Sans (UI) + JetBrains Mono (data)
"""

TERMINAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    /* ═══ Upstox Exact Brand Purple ═══ */
    --p:        #5B2ECC;
    --p2:       #4F1DB5;
    --p3:       #7B3FE4;
    --p4:       #9B66EE;
    --p-light:  #EDE8FD;
    --p-pale:   #F5F0FF;
    --p-bg:     rgba(91,46,204,0.06);
    --p-border: rgba(91,46,204,0.22);
    --p-glow:   rgba(91,46,204,0.28);
    --p-nav:    #2D1066;

    /* ═══ Surfaces ═══ */
    --bg:      #F7F8FA;
    --bg2:     #FFFFFF;
    --bg3:     #EEEEF5;
    --surface: #FFFFFF;
    --card:    #FFFFFF;

    /* ═══ Borders ═══ */
    --border:  #E4E4EE;
    --border2: #CCCCE0;

    /* ═══ Shadows ═══ */
    --sh-xs: 0 1px 3px rgba(0,0,0,0.05);
    --sh-sm: 0 2px 8px rgba(0,0,0,0.07);
    --sh-md: 0 4px 16px rgba(0,0,0,0.09);
    --sh-p:  0 4px 18px rgba(91,46,204,0.22);

    /* ═══ Semantic ═══ */
    --green:        #00B386;
    --green2:       #008F6C;
    --green-bg:     #E6F7F3;
    --green-border: rgba(0,179,134,0.3);
    --red:          #F45B69;
    --red2:         #D94255;
    --red-bg:       #FEF0F1;
    --red-border:   rgba(244,91,105,0.3);
    --gold:         #F59E0B;
    --gold2:        #D97706;
    --gold-bg:      #FEF3C7;
    --gold-border:  rgba(245,158,11,0.3);
    --blue:         #3B82F6;
    --blue-bg:      #EFF6FF;
    --teal:         #0891B2;
    --teal-bg:      #E0F7FA;
    --orange:       #F97316;

    /* ═══ Text ═══ */
    --tx:    #1A1A2E;
    --tx2:   #4A4A6A;
    --tx3:   #7A7A9A;
    --muted: #AAAABB;
    --white: #FFFFFF;

    /* ═══ Fonts ═══ */
    --f-ui:   'Plus Jakarta Sans', sans-serif;
    --f-mono: 'JetBrains Mono', monospace;
}

/* ══ BASE ══ */
html, body, [class*="css"] {
    font-family: var(--f-ui) !important;
    background:  var(--bg)  !important;
    color:       var(--tx)  !important;
    font-size: 14px;
}
.stApp { background: var(--bg) !important; }
* { box-sizing: border-box; }

::-webkit-scrollbar       { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg3); }
::-webkit-scrollbar-thumb { background:var(--border2); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:var(--p4); }

/* ══ TERMINAL HEADER ══ */
.terminal-header {
    background: var(--white);
    border-bottom: 1px solid var(--border);
    padding: 14px 28px 12px;
    position: relative;
    box-shadow: var(--sh-xs);
