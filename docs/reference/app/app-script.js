// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: */ //
// X E R X E S  ||  F I N A N C I A L   M O D E L I N G   S H E L L   */
// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: */
// EXPORT CONSOLE LOGS
(function() {
    const logBuffer = [];
    const methods = ['log', 'warn', 'error', 'debug', 'group', 'groupCollapsed', 'groupEnd'];
    let indentLevel = 0;

    // 1. CAPTURE EVERYTHING INTO A RAW STRING BUFFER
    methods.forEach(method => {
        const original = console[method];
        console[method] = function(...args) {
            const timestamp = new Date().toLocaleTimeString();
            const message = args.map(arg => 
                typeof arg === 'object' ? JSON.stringify(arg, null, 2) : arg
            ).join(' ');

            if (method === 'group' || method === 'groupCollapsed') {
                logBuffer.push({ method, timestamp, message: `>>> ${message}`, indent: indentLevel });
                indentLevel++;
            } else if (method === 'groupEnd') {
                indentLevel = Math.max(0, indentLevel - 1);
            } else {
                logBuffer.push({ method, timestamp, message, indent: indentLevel });
            }
            original.apply(console, args);
        };
    });

    window.exportLogs = function() {
        if (logBuffer.length === 0) return alert("No logs captured!");

        // Create a plain text version for copying (Indents preserved)
        const fullRawText = logBuffer.map(item => {
            const space = "  ".repeat(item.indent);
            return `[${item.timestamp}] [${item.method.toUpperCase()}] ${space}${item.message}`;
        }).join('\n');

        const overlay = document.createElement('div');
        overlay.id = 'log-viewer-overlay';
        overlay.style = "position:fixed;top:0;left:0;width:100%;height:100%;background:#1e1e1e;color:#d4d4d4;z-index:999999;font-family:monospace;overflow-y:auto;padding:20px;box-sizing:border-box;";

        overlay.innerHTML = `
            <div style="position:sticky;top:0;background:#252526;padding:10px;display:flex;gap:10px;border-bottom:2px solid #569cd6;z-index:10;">
                <button id="copyBtn" style="background:#4caf50;color:white;border:none;padding:12px;border-radius:4px;flex-grow:1;font-weight:bold;">COPY EVERYTHING (ALL GROUPS)</button>
                <button onclick="document.getElementById('log-viewer-overlay').remove()" style="background:#f44747;color:white;border:none;padding:12px;border-radius:4px;">CLOSE</button>
            </div>
            <pre id="displayArea" style="margin-top:20px; white-space:pre-wrap; font-size:12px;"></pre>
        `;

        document.body.appendChild(overlay);
        document.getElementById('displayArea').innerText = fullRawText;

        // One-tap copy for the entire raw text
        document.getElementById('copyBtn').onclick = function() {
            const textArea = document.createElement("textarea");
            textArea.value = fullRawText;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                const success = document.execCommand('copy');
                this.innerText = success ? "✅ COPIED TO CLIPBOARD!" : "❌ FAILED TO COPY";
                this.style.background = success ? "#2196F3" : "#f44747";
            } catch (err) {
                alert("Mobile restriction: Please manually select the text below and copy.");
            }
            document.body.removeChild(textArea);
        };
    };
})();
//////////////////////////////////////////////////////////////////
////////////////////////////////////// G L O B A L S |||||||||||||
const DEFAULT_MINIMUM_THRESHOLD = 5000;
const DEFAULT_SETTINGS = {
    defaultDiscount: 5,
    defaultFee: 1,
    defaultMinimum: 40,
    defaultMaximum: 50
};
const DEFAULT_FEED = {
    unit: 'MONTH',
    value: 1
};
const PRICE_ROUNDING_INTERVALS = [
    {
        limit: 5,
        interval: 0.01
    },
    {
        limit: 10,
        interval: 0.05
    },
    {
        limit: 25,
        interval: 0.1
    },
    {
        limit: 50,
        interval: 0.25
    },
    {
        limit: 100,
        interval: 0.5
    },
    {
        limit: 250,
        interval: 1
    },
    {
        limit: 500,
        interval: 2.5
    },
    {
        limit: 750,
        interval: 5
    },
    {
        limit: 1000,
        interval: 10
    },
    {
        limit: 2500,
        interval: 25
    },
    {
        limit: 5000,
        interval: 50
    },
    {
        limit: Infinity,
        interval: 100
    }
];
const SHARE_ROUNDING_INTERVALS = [
    {
        limit: 10,
        interval: 1
    },
    {
        limit: 100,
        interval: 5
    },
    {
        limit: 1000,
        interval: 10
    },
    {
        limit: 5000,
        interval: 25
    },
    {
        limit: 10000,
        interval: 50
    },
    {
        limit: Infinity,
        interval: 100
    }
];
const ACTIVE_SETTINGS_STRUCTURE = {
    activeDiscount: 0,
    activeFee: 0,
    activeMinimum: 0,
    activeMaximum: 0
};
const MARKET_HOLIDAYS_STRUCTURE = {
    name: 'string',
    type: 'full | half',
    anchorEpoch: 'number',
    preClose: 'number',
    postOpen: 'number'
};
const STORAGE_KEYS = {
    // ACTIVE
    ACTIVE_FEED: 'a.feed',
    ACTIVE_METRICS: 'a.metrics',
    ACTIVE_NEWS: 'a.news',
    ACTIVE_SETTINGS: 'a.settings',
    ACTIVE_TICKER: 'a.ticker',
    // DATA: API
    METRICS: (ticker, serial) => `metrics.${ticker}.${serial}`,
    NEWS: (ticker, feed) => `${ticker}.news.${feed}`,
    OVERVIEW: (ticker) => `overview.${ticker}`,
    // DATA: JSON
    MARKET_HOLIDAYS: 'd.market_holidays_v1',
    // INDEX
    INDEX_METRICS: (ticker) => `${ticker}.index.metrics`,
    INDEX_NEWS: (ticker) => `${ticker}.index.news`,
    // SYSTEM
    SESSION: 's.session',
    NEXT_EVENT: 's.next_event',
    NEXT_HOLIDAY: 's.next_holiday'
};
const METRICS_STRUCTURE = {
    // METRICS
    priceBid: 0,
    priceMinimum: 0,
    priceMaximum: 0,
    percentDiscount: 0,
    percentMinimum: 0,
    percentMaximum: 0,
    // PRICE TABLE: BLOCKS
    blockMin: 0,
    blockMinDouble: 0,
    blockMaxHalf: 0,
    blockMax: 0,
    // PRICE TABLE: COST
    costMin: 0,
    costMinDouble: 0,
    costMaxHalf: 0,
    costMax: 0,
    // PRICE TABLE: COMMS
    commsMin: 0,
    commsMinDouble: 0,
    commsMaxHalf: 0,
    commsMax: 0,
    // PRICE TABLE: TOTAL
    totalMin: 0,
    totalMinDouble: 0,
    totalMaxHalf: 0,
    totalMax: 0,
    // PRICE TABLE: SELL
    sellMin: 0,
    sellMinDouble: 0,
    sellMaxHalf: 0,
    sellMax: 0,
    // PRICE TABLE: PROFIT
    profitMin: 0,
    profitMinDouble: 0,
    profitMaxHalf: 0,
    profitMax: 0,
    // QUOTE DATA
    price: 0,
    change: 0,
    // SERIAL
    serial: ''
};
const NEWS_STRUCTURE = {
    articles: [
        {
        title: '',
        summary: '',
        source: '',
        url: '',
        image: '',
        label: '',
        relevance: 0,
        sentiment: 0,
        published: ''
        }
    ]
};
const OVERVIEW_STRUCTURE = {
    // COMPANY INFO
    name: '',
    exchange: '',
    sector: '',
    industry: '',
    country: '',
    website: '',
    // MARKET DATA
    marketCap: 0,
    weekHigh: 0,
    weekLow: 0,
    target: 0,
    // ANALYST RATINGS
    ratingStrongBuy: 0,
    ratingBuy: 0,
    ratingHold: 0,
    ratingSell: 0,
    ratingStrongSell: 0,
    ratingScore: 0,
    // DESCRIPTION
    description: ''
};
///////////////////////////////// F U N C T I O N S |||||||||||||
///// U T I L I T I E S |||||||||||||||||||||||||||||||||||||||||
// GLOBALS
let hideTimer = null;
let showTimer = null;
let lastUsedAllowHtml = false;
let lastMarketEventEpoch = null;
let lastHolidayEpoch = null;
// DISPLAY MESSAGE
window.displayMessage = function(text = '', opts = {}) {
    const anim = ANIMATION_TIMING;
    const cfg = Object.assign({
        type: 'info',
        loading: false,
        autoHideMs: anim.auto,
        allowHtml: false
    }, opts);
    const data = DOM.motherboard.data;
    const section = DOM.motherboard.section;
    const content = DOM.motherboard.content;
    // Clear outstanding timers
    if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
    }
    if (showTimer) {
        clearTimeout(showTimer);
        showTimer = null;
    }
    // Normalize flags
    const isVisible = Boolean(text);
    const shouldShowLoading = cfg.loading || cfg.type === 'loading';
    // Remove any previous type classes
    section.sectionMessage.classList.remove('msg--error', 'msg--info', 'msg--success', 'msg--loading');
    // Add new semantic modifier class (useful for styling)
    section.sectionMessage.classList.add(`msg--${cfg.type}`);
    // Loading indicator
    if (shouldShowLoading) {
        data.messageIndicator.classList.remove('hidden');
        data.messageIndicator.setAttribute('aria-hidden', 'false');
        data.messageIndicator.classList.add('spin'); // if you have a spinner animation class; optional
    } else {
        data.messageIndicator.classList.add('hidden');
        data.messageIndicator.setAttribute('aria-hidden', 'true');
        data.messageIndicator.classList.remove('spin');
    }
    // If we have a message to show
    if (isVisible) {
        // 1. Set text (immediately so screen readers pick it up)
        if (cfg.allowHtml) {
            data.messageText.innerHTML = text;
            lastUsedAllowHtml = true;
        } else {
            data.messageText.textContent = text;
            lastUsedAllowHtml = false;
        }
        // 2. Expand container (animation-expansion.expanded ->max-height transition)
        section.sectionMessage.classList.add('open');
        // 3. Make content container visible after expansion begins
        content.contentMessage.classList.add('in');
        // 4. Slight delay then reveal the text to match your other toggles (500ms)
        showTimer = setTimeout(() => {
            data.messageText.classList.add('in');
            showTimer = null;
        }, anim.t500);

        // If autoHide requested, schedule hide
        if (Number.isFinite(cfg.autoHideMs) && cfg.autoHideMs > 0) {
            hideTimer = setTimeout(() => {
                window.displayMessage('', {
                    type: 'info',
                    loading: false,
                    autoHideMs: null
                });
            }, cfg.autoHideMs);
        }
    } else {
        // 1. Remove visible class from text (start fading out the text)
        DOM.motherboard.data.messageText.classList.remove('in');
        // 2. After fade-out ends, collapse the container
        setTimeout(() => {
            data.contentMessage.classList.remove('in');
            // 3. Trigger collapse (this uses the CSS transition)
            section.sectionMessage.classList.remove('open');
            // 4. Remove half-speed class AFTER collapse animation
            setTimeout(() => {
                section.sectionMessage.classList.remove('half-speed');
            }, anim.t5000); // match the CSS slow-speed duration
        }, anim.t250);
    }
};
// DISPLAY MESSAGE HELPERS
window.displayMessageError = (text, ms) => displayMessage(text, {
    type: 'error',
    loading: false,
    autoHideMs: ms ?? 5000
});
window.displayMessageInfo = (text, ms) => displayMessage(text, {
    type: 'info',
    loading: false,
    autoHideMs: ms ?? 4000
});
window.displayMessageLoading = (text) => displayMessage(text, {
    type: 'loading',
    loading: true,
    autoHideMs: null
});
window.displayMessageSuccess = (text, ms) => displayMessage(text, {
    type: 'success',
    loading: false,
    autoHideMs: ms ?? 4000
});
window.hideMessage = () => displayMessage('', {
    type: 'info',
    loading: false,
    autoHideMs: null
});
// OBJECT LITERAL: DEBUG
const Debug = {
    enabled: true,
    group(label) {
        if (!this.enabled) return;
        console.groupCollapsed(label);
    },
    subgroup(label) {
        if (!this.enabled) return;
        console.groupCollapsed(label);
    },
    open(label) {
        if (!this.enabled) return;
        console.group(label);
    },
    log(...args) {
        if (!this.enabled) return;
        console.log(...args);
    },
    warn(...args) {
        if (!this.enabled) return;
        console.warn(...args);
    },
    error(...args) {
        if (!this.enabled) return;
        console.error(...args);
    },
    end() {
        if (!this.enabled) return;
        console.groupEnd();
    }
};
// OBJECT LITERAL: DATE CACHE
const DateCache = {
    PRECISION_SECONDS: {
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    },
    RANGE_MULTIPLIER: {
        day: 1,
        week: 0.75,
        minimonth: 0.75,
        month: 0.5,
        year: 0.25
    },
    RANGE_SECONDS: {
        day: 86400,
        week: 86400 * 7,
        month: 86400 * 30,
        year: 86400 * 365
    },
    // EXTERNAL
    external: {
        // LOAD JSON (ASYNC)
        async loadJSON(path) {
            try {
                const response = await fetch(path);
                return await response.json();
            } catch (error) {
                Debug.open('« ERROR: json »');
                Debug.error('Unable to load from JSON');
                throw error;
            }
        },
        // LOAD TEXT (ASYNC)
        async loadText(path) {
            try {
                const response = await fetch(path);
                return await response.text();
            } catch (error) {
                Debug.open('« ERROR: text »');
                Debug.error('Unable to load from TEXT file');
                throw error;
            }
        }
    },
    // HOLIDAYS
    holidays: {
        PATH: {
            relative: './data/holidays.json',
            android: '/storage/emulated/0/Files/Code/Code Editor/Mother/FMS/data/holidays.json',
            desktop: 'C:\\Files\\Developer\\VSCode\\Mother\\Area51\\data\\holidays.json',
        },
        STORAGE_KEY: STORAGE_KEYS.MARKET_HOLIDAYS,
        DAY: 86400,
        HOUR: 3600,
        MARKET_OPEN_UTC: {
            h: 14,
            m: 30
        },
        MARKET_CLOSE_UTC: {
            h: 21,
            m: 30
        },
        HOLIDAY_ANCHOR_UTC: {
            h: 18,
            m: 30
        },
        HOLIDAY_CACHE: null,
        // UTC DAY
        utcDay(epoch) {
            return new Date(epoch * 1000).getUTCDay(); // 0–6
        },
        // BUILD HOLIDAY ANCHOR
        buildHolidayAnchor(epoch) {
            const d = new Date(epoch * 1000);
            const anchor = Math.floor(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), this.HOLIDAY_ANCHOR_UTC.h, this.HOLIDAY_ANCHOR_UTC.m, 0) / 1000);
            return anchor;
        },
        // COMPUTE HOLIDAY BOUNDS
        computeHolidayBounds(holidaysArray) {
            if (!Array.isArray(holidaysArray)) {
                Debug.open('« ERROR »');
                Debug.warn('Invalid input: not array.');
                return [];
            }
            const result = holidaysArray.map(h => {
                const anchorEpoch = this.buildHolidayAnchor(h.epoch);
                const day = this.utcDay(anchorEpoch);
                const type = h.type === 'half' ? 'half' : 'full';
                let preClose;
                let postOpen;
                if (type === 'half') {
                    preClose = anchorEpoch;
                    postOpen = day === 5 ? anchorEpoch + (20 + 48) * this.HOUR : anchorEpoch + 20 * this.HOUR;
                } else {
                    if (day === 1) {
                        preClose = anchorEpoch - 69 * this.HOUR;
                        postOpen = anchorEpoch + 20 * this.HOUR;
                    } else if (day === 5) {
                        preClose = anchorEpoch - 21 * this.HOUR;
                        postOpen = anchorEpoch + 68 * this.HOUR;
                    } else {
                        preClose = anchorEpoch - 21 * this.HOUR;
                        postOpen = anchorEpoch + 20 * this.HOUR;
                    }
                }
                return {
                    name: h.name || '',
                    type,
                    anchorEpoch,
                    preClose,
                    postOpen
                };
            }).sort((a, b) => a.anchorEpoch - b.anchorEpoch);
            Debug.log('Count (output):', result.length);
            return result;
        },
        // ASYNC: LOAD AND NORMALIZE HOLIDAYS
        async importAndNormalizeHolidays() {
            Debug.log(' \nChecking device and storage path...');
            const getHolidaysPath = () => {
                const isAndroid = /Android/i.test(navigator.userAgent);
                Debug.log('Device is Android:', isAndroid);
                Debug.log('...checked device and storage path.\n ');
                return isAndroid ? this.PATH.relative : this.PATH.desktop;
            };
            const raw = await DateCache.external.loadJSON(getHolidaysPath());
            const holidaysArray = Object.values(raw).flat();
            Debug.log(' \nComputing holiday bounds...');
            const computed = this.computeHolidayBounds(holidaysArray);
            Debug.log('...computed holiday bounds.\n ');
            const shaped = computed.map(h => DateCache.structure.marketHoliday(h));
            this.HOLIDAY_CACHE = shaped;
            DateCache.save(this.STORAGE_KEY, shaped, 'static');
            Debug.log(' \nHolidays (raw):', holidaysArray.length);
            Debug.log('Holidays (cached):', shaped.length, '\n ');
            return shaped;
        },
        // ASYNC: GET HOLIDAY CALENDAR
        async getHolidayCalendar() {
            Debug.log(' \nGetting holiday calendar...');
            if (this.HOLIDAY_CACHE) {
                Debug.log('...got holiday calendar from cache.\n ');
                return this.HOLIDAY_CACHE;
            }
            const cached = DateCache.load(this.STORAGE_KEY);
            if (cached?.data && Array.isArray(cached?.data)) {
                this.HOLIDAY_CACHE = cached.data;
                Debug.log('...got holiday calendar from storage cache.\n ');
                return this.HOLIDAY_CACHE;
            }
            Debug.log('...no holiday calendar.');
            Debug.log(' \nImporting and normalizing holidays...');
            Debug.subgroup('{ Import and Normalize Holidays }');
            const result = await this.importAndNormalizeHolidays();
            Debug.end();
            Debug.log('...imported and normalized holidays.\n ');
            return result;
        },
        // FIND ACTIVE HOLIDAY
        findActiveHoliday(nowEpoch) {
            Debug.log(' \nFinding active holiday...');
            for (const h of this.HOLIDAY_CACHE) {
                if (nowEpoch >= h.preClose && nowEpoch < h.postOpen) {
                    Debug.log('...found active holiday.');
                    return h;
                }
                if (nowEpoch < h.preClose) break;
            }
            Debug.log('...not found active holiday.');
            return null;
        },
        // FIND NEXT HOLIDAY
        findNextHoliday(nowEpoch) {
            Debug.log('Finding next holiday...');
            const found = this.HOLIDAY_CACHE.find(h => h.preClose > nowEpoch);
            if (!found) {
                Debug.open('« WARNING »');
                Debug.warn('...next holiday not found.\n ');
                return null;
            } else {
                Debug.log('...found next holiday.\n ');
                return found;
            }
        },
        // GET HOLIDAY STATE
        getHolidayState(nowEpoch) {
            Debug.log(' \nGetting holiday state...');

            Debug.subgroup('{ Holiday State }');

            const active = this.findActiveHoliday(nowEpoch);
            const next = this.findNextHoliday(active ? active.postOpen : nowEpoch);

            Debug.subgroup('< Holiday Details >');
            Debug.log(' \nActive holiday:', active?.name || 'none');
            Debug.log(`Next holiday: ${next.name || 'none'}\n `);
            Debug.end();
            Debug.end();

            Debug.log('...got holiday state.\n ');

            return {
                active,
                next
            };
        }
    },
    // MARKET
    market: {
        OPEN_UTC: 14 * 3600 + 30 * 60,
        CLOSE_UTC: 21 * 3600 + 30 * 60,
        DAY: 86400,
        // IS WEEKEND
        isWeekend(epoch) {
            Debug.log(' \nChecking if today is a weekend...');
            const d = new Date(epoch * 1000).getUTCDay();
            Debug.log('...checked if today is a weekend.');
            return d === 0 || d === 6;
        },
        // GET TODAY OPEN CLOSE
        getTodayOpenClose(epoch) {
            Debug.log('Getting todays open and close...');

            const d = new Date(epoch * 1000);
            const y = d.getUTCFullYear();
            const m = d.getUTCMonth();
            const day = d.getUTCDate();
            const open = Math.floor(Date.UTC(y, m, day, 14, 30, 0) / 1000);
            const close = Math.floor(Date.UTC(y, m, day, 21, 30, 0) / 1000);

            Debug.log('...got todays open and close.\n ');
            return {
                open,
                close
            };
        },
        // GET STATE
        getState(nowEpoch) {
            Debug.group('[ GET STATE ]');

             // PHASE 1: holiday override
            const holidays = DateCache.holidays.getHolidayState(nowEpoch);
            const isHoliday = holidays.active !== null;
            if (holidays.active) {
                Debug.end();
                return {
                    isOpen: false,
                    nextEvent: {
                        type: 'open',
                        epoch: holidays.active.postOpen
                    },
                    holidays
                };
            }

            Debug.log(' \nGetting market state...');
            Debug.subgroup('{ Market State }');

            // PHASE 2: weekend check
            const isWeekend = this.isWeekend(nowEpoch);
            if (isWeekend) {
                const {
                    open
                } = this.getTodayOpenClose(nowEpoch);
                let nextOpen = open;
                while (this.isWeekend(nextOpen)) {
                    nextOpen += this.DAY;
                }
                Debug.log('Next open (epoch):', nextOpen);
                Debug.log('Next open (PH):', formatDateTime(nextOpen, 'MNL'));
                Debug.end();
                Debug.end();
                return {
                    isOpen: false,
                    nextEvent: {
                        type: 'open',
                        epoch: nextOpen
                    },
                    holidays
                };
            }

            // PHASE 3: Weekday trading hours
            const {
                open,
                close
            } = this.getTodayOpenClose(nowEpoch);

            Debug.subgroup('< Market Details >');

            let isOpen = false;
            let nextEvent = null;
            let nowLog = '';
            if (nowEpoch >= open && nowEpoch < close) {
                isOpen = true;
                nextEvent = {
                    type: 'Market close',
                    epoch: close
                };
                nowLog = 'Market open';
            } else if (nowEpoch < open) {
                nextEvent = {
                    type: 'Market open',
                    epoch: open
                };
                nowLog = 'Pre-market';
            } else {
                nextEvent = {
                    type: 'Market open',
                    epoch: open + this.DAY
                };
                nowLog = 'After-hours';
            }

            // PHASE 4: Upcoming holiday pre-close
            if (holidays.next && holidays.next.preClose < nextEvent.epoch) {
                Debug.log('Pre-close override:', holidays.next.name);
                nextEvent = {
                    type: 'Market close',
                    epoch: holidays.next.preClose
                };
            }

            Debug.log(' \nMarket is open:', isOpen);
            Debug.log('Today is a holiday:', isHoliday);
            Debug.log('Today is a weekend:', isWeekend);
            Debug.log(`Current state: ${nowLog}\n `);

            Debug.subgroup('< Next Market Event Details >');
            Debug.log(' \nNext type:', nextEvent.type);
            Debug.log('Next date:', nextEvent.epoch);
            Debug.log(`${formatDateTime(nextEvent.epoch, 'MNL')}\n `);
            Debug.end();

            Debug.subgroup('< Open and Close Times >');
            Debug.log(' \nOpen (epoch):', open);
            Debug.log(formatDateTime(open, 'MNL'));
            Debug.log('Close (epoch):', close);
            Debug.log(`${formatDateTime(close, 'MNL')}\n `);
            Debug.end();
            Debug.end();

            Debug.end();
            Debug.log('...got market state.\n ');

            Debug.end();
            return {
                isOpen,
                nextEvent,
                holidays
            };
        }
    },
    // COUNTDOWN
    countdown: {
        CountdownPrecision: {
            SECOND: {
                unit: 'second',
                value: 1,
                label: 'second'
            },
            MINUTE: {
                unit: 'minute',
                value: 60,
                label: 'minute'
            },
            HOUR: {
                unit: 'hour',
                value: 3600,
                label: 'hour'
            },
            DAY: {
                unit: 'day',
                value: 86400,
                label: 'day'
            }
        },
        CountdownThresholds: [
            {
                remaining: 2, 
                precision: {
                    unit: 'day',
                    value: 86400,
                    label: 'day'
                },
                interval: 86400
            },
            {
                remaining: 2,
                precision: {
                    unit: 'hour',
                    value: 3600,
                    label: 'hour'
                },
                interval: 3600
            },
            {
                remaining: 2,
                precision: {
                    unit: 'hour',
                    value: 3600,
                    label: 'hour'
                },
                interval: 900
            },
            {
                remaining: 15,
                precision: {
                    unit: 'minute',
                    value: 60,
                    label: 'minute'
                },
                interval: 300
            },
            {
                remaining: 5,
                precision: {
                    unit: 'minute',
                    value: 60,
                    label: 'minute'
                },
                interval: 60
            },
            {
                remaining: 2,
                precision: {
                    unit: 'minute',
                    value: 60,
                    label: 'minute'
                },
                interval: 15
            },
            {
                remaining: 1,
                precision: {
                    unit: 'minute',
                    value: 60,
                    label: 'minute'
                },
                interval: 5
            },
            {
                remaining: 15,
                precision: {
                    unit: 'second',
                    value: 1,
                    label: 'second'
                },
                interval: 1
            }
        ],
        // GET COUNTDOWN INTERVAL
        getCountdownInterval(secondsRemaining) {
            for (const threshold of this.CountdownThresholds) {
                const thresholdSeconds = threshold.remaining * threshold.precision.value;
                if (secondsRemaining >= thresholdSeconds) {
                    return threshold.interval;
                }
            }
            return 1;
        },
        // GET COUNTDOWN INTERVAL
        getCountdownLabel(secondsRemaining) {
            for (const threshold of this.CountdownThresholds) {
                const thresholdSeconds = threshold.remaining * threshold.precision.value;
                if (secondsRemaining >= thresholdSeconds) {
                    return threshold.precision.label;
                }
            }
            return 1;
        },
        // FORMAT COUNTDOWN
        formatCountdown(secondsRemaining) {
            const days = Math.floor(secondsRemaining / 86400);
            const hours = Math.floor((secondsRemaining % 86400) / 3600);
            const minutes = Math.floor((secondsRemaining % 3600) / 60);
            const seconds = secondsRemaining % 60;
            // ≥ 2 days → days only
            if (days >= 2) {
                return `${days} days`;
            }
            // < 2 days but ≥ 24h → hours only
            if (days === 1) {
                return `${hours + 24} hours`;
            }
            // < 2 hours → hours + minutes
            if (hours >= 1) {
                return minutes > 0 ? `${hours} hour${hours !== 1 ? 's' : ''} ${minutes} minutes` : `${hours} hour${hours !== 1 ? 's' : ''}`;
            }
            // < 1 hour → minutes
            if (minutes >= 1) {
                return `${minutes} minutes`;
            }
            // final seconds
            return `${seconds} seconds`;
        },
        // COUNTDOWN MANAGER CLASS
        CountdownManager: class {
            constructor(targetEpoch) {
                Debug.group('{ Countdown Manager: Constructor }');
                this.targetEpoch = targetEpoch;
                this.intervalId = null;
                this.callbacks = [];
                Debug.log(' \nTarget epoch:', targetEpoch);
                Debug.log(formatDateTime(targetEpoch, 'MNL') + '\n ');
                Debug.end();
            }
            // START
             start() {
                Debug.subgroup('{ Start }');
                this.update();
                this.scheduleNext();
                Debug.end();
            }
            // UPDATE
            update() {
                Debug.log(' \nUpdating...');
                const now = Math.floor(Date.now() / 1000);
                Debug.subgroup('< Update Details >');
                Debug.log(' \nNow:', now);
                Debug.log(formatDateTime(now, 'MNL') + '\n ');
                const remaining = this.targetEpoch - now;
                if (remaining <= 0) {
                    this.stop();
                    this.notify({
                        expired: true,
                        remaining: 0
                    });
                    Debug.log('Expired:', true);
                    Debug.end();
                    Debug.log('...updated.\n ');
                    return;
                }
                const formatted = DateCache.countdown.formatCountdown(remaining);
                this.notify({
                    expired: false,
                    remaining,
                    formatted
                });
                Debug.end();
                Debug.log('...updated.\n ');
            }
            // SCHEDULE NEXT
            scheduleNext() {
                Debug.log(' \nScheduling next...');
                const now = Math.floor(Date.now() / 1000);
                const remaining = this.targetEpoch - now;
                const intervalSeconds = DateCache.countdown.getCountdownInterval(remaining);
                const intervalMs = intervalSeconds * 1000;
                const intervalLabel = DateCache.countdown.getCountdownLabel(remaining);
                Debug.subgroup('< Next Schedule Details >');
                Debug.log(' \nNow:', now);
                Debug.log('Remaining:', remaining);
                Debug.log(`Next interval (s): ${intervalSeconds} (${intervalLabel})\n `);
                Debug.end();
                this.intervalId = setTimeout(() => {
                    this.update();
                    this.scheduleNext();
                }, intervalMs);
                Debug.log('...scheduled next.\n ');
            }
            // STOP
            stop() {
                Debug.log(' \nStopping...');
                if (this.intervalId) {
                    clearTimeout(this.intervalId);
                    this.intervalId = null;
                    Debug.log('Timer cleared.');
                } else {
                    Debug.log('No active timer.');
                }
                Debug.log('...stopped.\n ');
            }
            // ON UPDATE
            onUpdate(callback) {
                Debug.log(' \nOn Updating...');
                this.callbacks.push(callback);
                Debug.log('Callback count:', this.callbacks.length);
                Debug.log('...on updated.\n ');
            }
            // NOTIFY
            notify(data) {
                Debug.log('Notifying...');
                Debug.subgroup('< Notify Details >');
                Debug.log(' \nCallbacks:', this.callbacks.length);
                Debug.log('Expired:', data.expired);
                Debug.log('Remaining:', data.remaining);
                Debug.log('Formatted:', data.formatted + '\n ');
                Debug.end();
                this.callbacks.forEach(cb => cb(data));
                Debug.log('...notified.\n ');
            }
        },
        // COUNTDOWN MODULE
        countdown: {
            managers: new Map(),
            // START
            start(key, targetEpoch, callback) {
                Debug.group(`[ COUNTDOWN: Start ] → ${key}`);
                if (this.managers.has(key)) {
                    Debug.log(' \nExisting manager found → stopping.');
                    this.managers.get(key).stop();
                }
                const manager = new DateCache.countdown.CountdownManager(targetEpoch);
                manager.onUpdate(callback);
                manager.start();
                this.managers.set(key, manager);
                Debug.log(' \nActive managers:', this.managers.size, '\n ');
                Debug.end();
            },
            // STOP
            stop(key) {
                Debug.subgroup(`{ STOP } → ${key}`);
                if (this.managers.has(key)) {
                    this.managers.get(key).stop();
                    Debug.log(' \nExisting manager stopped:', key);
                    this.managers.delete(key);
                    Debug.log('Key deleted.');
                } else {
                    Debug.open('‹ WARNING ›');
                    Debug.warn('No manager for key:', key);
                }
                Debug.log(' \nActive managers:', this.managers.size, '\n ');
                Debug.end();
            }
        }
    },
    // STRUCTURE
    structure: {
        // MARKET HOLIDAYS
        marketHoliday: function(h) {
            if (!h || typeof h !== 'object') {
                Debug.open('« ERROR: market holidays structure »');
                Debug.error('Invalid input: holidays data required.');
                throw new Error('Invalid input: holidays data required.');
            }
            return {
                name: h.name || '',
                type: h.type === 'half' ? 'half' : 'full',
                anchorEpoch: Number(h.anchorEpoch) || 0,
                preClose: Number(h.preClose) || 0,
                postOpen: Number(h.postOpen) || 0
            };
        },
        // METRICS
        metrics: function(metricsRaw, price, change) {
            if (!metricsRaw || typeof price !== 'number') {
                Debug.open('« ERROR: metrics structure »');
                Debug.error('Invalid input: metrics data required.');
                throw new Error('Invalid input: metrics data required.');
            }
            return {
                // METRICS (NUMERIC, UNFORMATTED)
                priceBid: metricsRaw.priceBid,
                priceMinimum: metricsRaw.priceMinimum,
                priceMaximum: metricsRaw.priceMaximum,
                percentDiscount: metricsRaw.percentDiscount,
                percentMinimum: metricsRaw.percentMinimum,
                percentMaximum: metricsRaw.percentMaximum,
                // BLOCKS
                blockMin: metricsRaw.blockMin,
                blockMinDouble: metricsRaw.blockMinDouble,
                blockMaxHalf: metricsRaw.blockMaxHalf,
                blockMax: metricsRaw.blockMax,
                // COST
                costMin: metricsRaw.costMin,
                costMinDouble: metricsRaw.costMinDouble,
                costMaxHalf: metricsRaw.costMaxHalf,
                costMax: metricsRaw.costMax,
                // COMMISSIONS
                commsMin: metricsRaw.commsMin,
                commsMinDouble: metricsRaw.commsMinDouble,
                commsMaxHalf: metricsRaw.commsMaxHalf,
                commsMax: metricsRaw.commsMax,
                // TOTAL
                totalMin: metricsRaw.totalMin,
                totalMinDouble: metricsRaw.totalMinDouble,
                totalMaxHalf: metricsRaw.totalMaxHalf,
                totalMax: metricsRaw.totalMax,
                // SELL
                sellMin: metricsRaw.sellMin,
                sellMinDouble: metricsRaw.sellMinDouble,
                sellMaxHalf: metricsRaw.sellMaxHalf,
                sellMax: metricsRaw.sellMax,
                // PROFIT
                profitMin: metricsRaw.profitMin,
                profitMinDouble: metricsRaw.profitMinDouble,
                profitMaxHalf: metricsRaw.profitMaxHalf,
                profitMax: metricsRaw.profitMax,
                // QUOTE market (RAW)
                price: price,
                change: change,
                // SERIAL
                serial: metricsRaw.serial || ''
            };
        },
        // NEWS
        news: function(sortedFeed) {
            return {
                articles: sortedFeed.map(article => ({
                    title: article.title || '',
                    summary: article.summary || '',
                    source: article.source || '',
                    url: article.url || '',
                    image: article.banner_image || '',
                    label: article.overall_sentiment_label || '',
                    relevance: article.relevance_score || '0',
                    sentiment: article.overall_sentiment_score || '0',
                    published: article.time_published || ''
                }))
            };
        },
        // OVERVIEW
        overview: function(overviewRaw, ratingResult) {
            if (!overviewRaw) {
                Debug.open('« ERROR: overview structure »');
                Debug.error('Invalid input: overview data required.');
                throw new Error('Invalid input: overview data required');
            }
            const ratingScore = Number(ratingResult?.score) || 0;
            return {
                // ---- COMPANY INFO ----
                name: overviewRaw.name || '',
                exchange: overviewRaw.exchange || '',
                sector: overviewRaw.sector || '',
                industry: overviewRaw.industry || '',
                country: overviewRaw.country || '',
                website: overviewRaw.website || '',
                // ---- MARKET DATA ----
                marketCap: overviewRaw.marketCap || 0,
                weekHigh: overviewRaw.weekHigh || 0,
                weekLow: overviewRaw.weekLow || 0,
                target: overviewRaw.target || 0,
                // ---- ANALYST RATINGS (FLAT) ----
                ratingStrongBuy: overviewRaw.ratings?.strongBuy || 0,
                ratingBuy: overviewRaw.ratings?.buy || 0,
                ratingHold: overviewRaw.ratings?.hold || 0,
                ratingSell: overviewRaw.ratings?.sell || 0,
                ratingStrongSell: overviewRaw.ratings?.strongSell || 0,
                // ---- DERIVED ----
                ratingScore: ratingScore,
                // ---- DESCRIPTION ----
                description: overviewRaw.description || ''
            };
        }
    },
    // SAVE
    save(key, data, type) {
        Debug.subgroup(`{ Date Cache: Save } → ${key}`);
        if (!key || typeof key !== 'string') {
            Debug.open('« ERROR: DateCache.save »');
            Debug.error('Invalid key:', key);
            Debug.end();
            throw new Error('Invalid key:', key);
        }
        var now = Math.floor(Date.now() / 1000);
        var cache = {
            data: data,
            timestamp: null,
            expiry: null,
            type: type
        };
        if (type === 'static') {
            Debug.log(' \nType: static');
        }
        else if (type === 'fixed') {
            if (!data || typeof data.epoch !== 'number') {
                Debug.open('« ERROR: DateCache.save »');
                Debug.error('Fixed data type invalid or missing epoch date.');
                Debug.warn('No data saved.');
                Debug.end();
                throw new Error('Invalid data type or missing epoch date. \nFixed type requires epoch date. \nNo data saved.');
            }
            cache.timestamp = now;
            cache.expiry = data.epoch;
            Debug.log(' \nType: Fixed');
        }
        else if (type === 'relative') {
            var range = DateCache.getRelativeRange(key, data);
            if (typeof range !== 'number' || range <= 0) {
                Debug.open('« ERROR: DateCache.getRelativeRange »');
                Debug.error('Invalid or missing date-range:', range);
                Debug.warn('No data saved.');
                Debug.end();
                throw new Error('Invalid or missing date-range. \nNo data saved.');
            }
            cache.timestamp = now;
            cache.expiry = now + range;
            Debug.log(' \nType: Relative');
        }
        else {
            Debug.open('« ERROR: DateCache.save »');
            Debug.error(' \nUnknown error: no data saved.\n ');
            Debug.end();
            throw new Error(`Unknown error: no data saved.`);
        }
        Debug.log('Timestamp:', cache.timestamp);
        Debug.log('Expiry:', cache.expiry, '\n ');
        Debug.end();
        localStorage.setItem(key, JSON.stringify(cache));
    },
    // GET RELATIVE RANGE
    getRelativeRange(key, data) {
        Debug.log('Getting relative range...');
        let rel = 0;
        switch (key) {
            case 'overview':
                rel = 86400 * 30;
                Debug.log('...got relative overview range:', rel);
                return rel;
            case 'news':
                rel = Number(data.rangeSeconds) || 0;
                Debug.log('...got relative news range:', rel);
                return rel;
            default:
                Debug.log('...got relative range:', rel);
                return rel;
        }
    },
    // LOAD
    load(key) {
        Debug.subgroup(`{ Date Cache: Load } → ${key}`);
        if (!key || typeof key !== 'string') {
            Debug.open('« ERROR: DateCache.load »');
            Debug.error('Invalid key:', key);
            Debug.end();
            throw new Error('Invalid key:', key);
        }
        const stored = localStorage.getItem(key);
        if (!stored) {
            Debug.log(' \nItem not stored: no data loaded.\n ');
            Debug.end();
            return null;
        }
        let cache;
        try {
            cache = JSON.parse(stored);
        } catch {
            localStorage.removeItem(key);
            Debug.open('‹ WARNING: DateCache.load ›');
            Debug.warn('Corrupt data:', key);
            Debug.end();
            return null;
        }
        const now = Math.floor(Date.now() / 1000);
        const expired = cache.expiry !== null && now >= cache.expiry;
        Debug.log('Data expired:', expired);
        Debug.end();
        return {
            data: cache.data,
            expired,
            timestamp: cache.timestamp || null,
            expiry: cache.expiry || null,
            type: cache.type
        };
    },
    // METRICS
    metrics: {
        // GENERATE SERIAL
        generateSerial(ticker, settings, nextEventEpoch) {
            console.log('Generating serial...');
            // Example: "AAPL_v5.1.4050.1712345600"
            const settingsKey = `${settings.activeDiscount}.${settings.activeFee}.${settings.activeMinimum}${settings.activeMaximum}`;
            const serial = `${ticker}_v${settingsKey}.${nextEventEpoch}`;
            Debug.log(`...generated serial: ${serial}`);
            return serial;
        },
        // SAVE METRICS
        saveMetrics(ticker, serial, metricsData) {
            Debug.log('Saving metrics...');
            if (!ticker || !serial || !metricsData) {
                Debug.open('« ERROR: DateCache.metrics.saveMetrics »');
                Debug.error('Invalid input.');
                Debug.warn('No data saved.');
                throw new Error('Invalid input \nNo data saved.');
            }
            const metricsKey = STORAGE_KEYS.METRICS(ticker);
            const indexKey = STORAGE_KEYS.INDEX_METRICS(ticker);
            const now = Math.floor(Date.now() / 1000);
            const cache = {
                serial,
                data: metricsData,
                timestamp: now
            };
            // Metrics validity is SERIAL-based, not time-based
            DateCache.save(cacheKey, cache, 'fixed');
            Debug.log('Saved data: metrics');
            // Update metrics index
            let index = DateCache.load(indexKey);
            let serials = Array.isArray(index?.data) ? index.data : [];
            if (!serials.includes(serial)) {
                serials.push(serial);
                DateCache.save(indexKey, serials, 'fixed');
                Debug.log('Saved data: serial');
            }
            Debug.log('...saved metrics.');
        },
        // FIND METRICS BY SERIAL
        findMetricsBySerial(ticker, targetSerial) {
            Debug.log('Finding metrics by serial...');
            const metricsKey = STORAGE_KEYS.METRICS(ticker);
            const cached = DateCache.load(metricsKey);
            if (cached && cached.data && cached.data.data && cached.data.serial === targetSerial) {
                Debug.log('...found metrics by serial.');
                return cached.data;
            }
            Debug.open('‹ WARNING: DateCache.metrics.findMetricsBySerial ›');
            Debug.warn('No metrics found.');
            return null;
        },
        // CLEAN UP INDEX - I N C O M P L E T E
        cleanupIndex(ticker) {
            Debug.log('Cleaning up index...');
            const indexKey = STORAGE_KEYS.INDEX_METRICS(ticker);
            const index = DateCache.load(indexKey);
            if (!index || !index.data) {
                Debug.open('‹ WARNING: DateCache.metrics.cleanupIndex ›');
                Debug.warn('...cleanup failed.');
                return null;
            } else {
                Debug.log('...cleaned up index.');
            }
            // Implementation would check each serial's validity
            // and remove stale entries. For Phase 1, this can be a placeholder.
        }
    }
};
// WAIT
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
// WAIT FOR TRANSITION
function waitForTransition(el, caller = '') {
    return new Promise(resolve => {
        // READ COMPUTED TRANSITION VALUES
        const style = getComputedStyle(el);
        const durations = style.transitionDuration.split(',').map(v => parseFloat(v) || 0);
        const delays = style.transitionDelay.split(',').map(v => parseFloat(v) || 0);

        const duration = Math.max(...durations);
        const delay = Math.max(...delays);
        const total = duration + delay;

        // NO TRANSITION
        if (total === 0 || style.transitionProperty === 'none') {
            resolve({
                element: el.id,
                duration: duration * 1000,
                delay: delay * 1000,
                total: total * 1000,
                endedByEvent: false,
                reason: 'none'
            });
            return;
        }

        const startRect = el.getBoundingClientRect();
        const startOpacity = style.opacity;

        let finished = false;
        let fallbackTimer;

        const finish = (result) => {
            if (finished) return;
            finished = true;
            clearTimeout(fallbackTimer);
            resolve(result);
        };

        const onEnd = (e) => {
            if (e.target !== el) return;
            el.removeEventListener('transitionend', onEnd);

            finish({
                caller: caller,
                element: el.id,
                duration: duration * 1000,
                delay: delay * 1000,
                total: total * 1000,
                endedByEvent: true,
                reason: 'event'
            });
        };

        el.addEventListener('transitionend', onEnd);

        fallbackTimer = setTimeout(() => {
            el.removeEventListener('transitionend', onEnd);

            const endRect = el.getBoundingClientRect();
            const endOpacity = getComputedStyle(el).opacity;
            const moved = Math.abs(startRect.left - endRect.left) > 0.5 || Math.abs(startRect.top - endRect.top) > 0.5;
            const opacityChanged = startOpacity !== endOpacity;

            let reason;

            if (moved && opacityChanged) {
                reason = 'interrupted';
            } else if (!moved && !opacityChanged) {
                reason = 'failed';
            } else {
                reason = 'fallback';
            }

            finish({
                caller: caller,
                element: el.id,
                duration: duration * 1000,
                delay: delay * 1000,
                total: total * 1000,
                endedByEvent: false,
                reason
            });

        }, total * 1000 + 50);
    });
}
///////////////////////////////// F O R M A T E R S |||||||||||||
///// F O R M A T T E R S |||||||||||||||||||||||||||||||||||||||
// GLOBALS
const REGIONS = {
    LAX: "America/Los_Angeles", // US Pacific (UTC-8/7)
    NYC: "America/New_York",    // US Eastern (UTC-5/4)
    UTC: "UTC",                 // Universal standard
    LON: "Europe/London",       // United Kingdom (UTC+0/1)
    PAR: "Europe/Paris",        // Mainland Europe (UTC+1/2)
    JNB: "Africa/Johannesburg", // South Africa (UTC+2)
    MOW: "Europe/Moscow",       // Russia (UTC+3)
    DXB: "Asia/Dubai",          // UAE (UTC+4)
    HKG: "Asia/Hong_Kong",      // Hong Kong (UTC+8)
    MNL: "Asia/Manila",         // Philippines (UTC+8)
    TYO: "Asia/Tokyo",          // Japan (UTC+9)
};
// FORMAT DATE TIME
function formatDateTime(epoch, code = 'UTC', type = 'full') {
    const len = epoch.toString().length;

    let multiplier = 1;

    if (len === 10) {
        multiplier = 1000;
    } else {
        multiplier = 1;
    }

    const date = new Date(epoch * multiplier);
    const inputKey = String(code).toUpperCase();

    let primaryKey = REGIONS[inputKey] && !REGIONS[inputKey].includes('/') ? REGIONS[inputKey] : inputKey;
    let formattedDateTime = '';

    const ianaZone = REGIONS[primaryKey] || REGIONS.UTC;

    if (!REGIONS[primaryKey]) primaryKey = 'UTC';
    if (type === 'full') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'short', 
            day:          '2-digit', 
            month:        'short', 
            year:         'numeric',
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       false, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'full24') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'short', 
            day:          '2-digit', 
            month:        'short', 
            year:         'numeric',
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       true, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'fullLong') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'long', 
            day:          '2-digit', 
            month:        'long', 
            year:         'numeric',
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       false, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'fullLong24') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'long', 
            day:          '2-digit', 
            month:        'long', 
            year:         'numeric',
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       true, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'date') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'short', 
            day:          '2-digit', 
            month:        'short', 
            year:         'numeric',
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'dateLong') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            weekday:      'long', 
            day:          '2-digit', 
            month:        'long', 
            year:         'numeric',
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'dateNum') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            year:       'numeric',
            month:      '2-digit',
            day:        '2-digit',
            hour12:     false, 
            timeZone:   ianaZone
          }).format(date);
    } else if (type === 'time') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            hour:         '2-digit', 
            minute:       '2-digit', 
            hour12:       false, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'time24') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            hour:         '2-digit', 
            minute:       '2-digit', 
            hour12:       true, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'timeFull') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       false, 
            timeZone:     ianaZone
          }).format(date);
    } else if (type === 'timeFull24') {
        formattedDateTime = new Intl.DateTimeFormat('en-PH', {
            hour:         '2-digit', 
            minute:       '2-digit', 
            second:       '2-digit',
            hour12:       true, 
            timeZone:     ianaZone
          }).format(date);
    } else {
        formattedDateTime = 'YYYY-MM-DD, hh:mm:ss ampm';
        Debug.warn('Incorrect date type.');
    }

    return `${formattedDateTime} ${primaryKey}`;
}
// TO CAPITAL CASE
function toCapitalCase(string) {
    Debug.log(` \nConverting ${string} to capital case\n `);
    return string.charAt(0).toUpperCase() + string.slice(1);
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// F E T C H |||||||||||||||||||||||||||||||||||||||||||||||||
// GLOBALS
const ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query?';
const API_KEYS = [
    'ONWS7QAI76ZRNLON',
    'XWS4ONTT61PC2PB2',
    '7JXAQ3E7L87TUD8C',
    'F6QSTYW37EJ5ADT4',
    'H1WS1PXIG3RU8SGE',
    '2DZO5IHJECQ3171Z',
    'ZX5OF44FKO747741'
];
const API_RESPONSES = {
    burst: [
        "1 request per second",
        "per-second burst",
        "consider spreading",
        "API requests more sparingly"
    ],
    daily: [
        "25 requests per day",
        "We have detected your API key",
        "standard API rate limit"
    ]
};
let currentKeyIndex = 0;
// GET NEXT API KEY
function getNextApiKey() {
    let key = null;
    try {
        if (!API_KEYS?.length) {
            Debug.log('❌ No API_KEYS configured');
            throw new Error('❌ No API_KEYS configured');
        }

        if (!window.failedKeys) window.failedKeys = new Set();

        if (window.failedKeys.size >= API_KEYS.length) {
            Debug.log('🕒 API keys exceeded daily limit!');
            throw new Error('🕒 API keys exceeded daily limit!');
        }

        for (const k of API_KEYS) {
            if (!window.failedKeys.has(k)) {
                Debug.log(`✅ API key: ${k}`);
                key = k;
                break;
            }
        }
    } catch (e) {
        Debug.error(e.message);
    } finally {
        if (key === null) {
            Debug.log(`⚠️ API key (fallback): ${API_KEYS[0]}`);
            key = API_KEYS[0];
        }
    }

    return key;
}
// MARK KEY AS FAILED
function markKeyAsFailed(apiKey) {
    if (!window.failedKeys) window.failedKeys = new Set();
    window.failedKeys.add(apiKey);
    currentKeyIndex = (currentKeyIndex + 1) % API_KEYS.length;

    Debug.log(`❌ Failed key: ${apiKey}`);
}
// ASYNC: FETCH ALPHA VANTAGE NEWS
async function fetchAlphaVantageNews(ticker, rangeUnit, rangeValue) {
    Debug.group(`[ FETCH NEWS ] ${ticker} ${rangeUnit}_${rangeValue}`);

    const RANGE_TO_SECONDS = {
        DAY: 86400,
        WEEK: 604800,
        MONTH: 2592000,
        YEAR: 31536000
    };
    let valog = '';

    // INPUT VALIDATION
    if (!ticker || typeof ticker !== 'string') {
        valog = `❌ Invalid ticker: ${ticker}`;
        throw new Error('❌ Parameter(s) invalid');
    }
    if (!RANGE_TO_SECONDS[rangeUnit]) {
        valog = `❌ Invalid range unit: ${rangeUnit}`;
        Debug.end();
        throw new Error('❌ Parameter(s) invalid');
    }
    if (!Number.isInteger(rangeValue) || rangeValue <= 0) {
        valog = `❌ Invalid range value: ${rangeValue}`;
        throw new Error('❌ Parameter(s) invalid');
    }
    Debug.subgroup('{ Input validation }');
    Debug.error(valog);
    Debug.end();

    // EPOCH CALCULATION, TIME-FROM CONVERSION AND EXPIRY CALCULATION
    const symbol = ticker.trim().toUpperCase();
    const nowEpoch = Math.floor(Date.now() / 1000);
    const secondsBack = RANGE_TO_SECONDS[rangeUnit] * rangeValue;
    const fromEpoch = nowEpoch - secondsBack;

    // CALCULATE TIME-FROM
    function toAlphaVantageTimeFrom(epochSeconds) {
        const date = new Date(epochSeconds * 1000);
        const pad = n => String(n).padStart(2, '0');
        const timeFrom = `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}`;
        return timeFrom;
    }
    const timeFrom = toAlphaVantageTimeFrom(fromEpoch);
    Debug.subgroup('{ Date range }');
    Debug.log(`Ticker symbol: ${symbol}`);
    Debug.log(`Epoch now: ${nowEpoch}`);
    Debug.log(`Seconds back: ${secondsBack}`);
    Debug.log(`Epoch from:  ${fromEpoch}`);
    Debug.log(`Time from: ${timeFrom}`);
    Debug.end();

    // COMPUTE NEXT EXPIRY
    function computeNewsExpiry(timestamp, timeFrom, unit, value) {
        const timeframe = timestamp - timeFrom;
        let multiplier;
        if (unit === 'DAY') {
            multiplier = 1.0;
        } else if (unit === 'WEEK') {
            multiplier = 0.75;
        } else if (unit === 'MONTH') {
            multiplier = value < 6 ? 0.75 : 0.5;
        } else if (unit === 'YEAR') {
            multiplier = 0.25;
        } else {
            multiplier = 0.75;
        }
        const expiry = Math.floor(timestamp + (timeframe * multiplier));
        return expiry;
    }

    // FETCH NEWS SENTIMENT
    let attempts = 0;
    const maxAttempts = API_KEYS.length;

    // DETECT NULL METRICS
    function detectNullMetrics(articles) {
        return articles.some(a => a.sentimentScore === null || a.relevanceScore === null);
    }
    while (attempts < maxAttempts) {
        const apiKey = getNextApiKey();
        Debug.subgroup(`{ Attempt ${attempts + 1} }`);
        Debug.log('apiKey:', apiKey);

        // VALIDATE API KEY
        if (!apiKey) {
            Debug.open(' [ ERROR: Fetch News ]');
            Debug.error('❌ No API key available');
            Debug.end();
            break;
        }
        const url = `${ALPHA_VANTAGE_BASE_URL}function=NEWS_SENTIMENT&sort=RELEVANCE&time_from=${timeFrom}&tickers=${encodeURIComponent(symbol)}&apikey=${apiKey}`;
        Debug.log('url = ', url);
        try {
            const response = await fetch(url);
            const data = await response.json();

            // VERIFY RAW DATA
            if (data?.Note || data?.['Error Message']) {
                Debug.warn('⚠️ API error → rotating key');
                markKeyAsFailed(apiKey);
                attempts++;
                Debug.end();
                continue;
            }
            Debug.end();

            Debug.subgroup('{ Normalization }');
            Debug.log('feed length:', feed.length);

            // TRIM AND NORMALIZE RAW DATA
            const feed = Array.isArray(data?.feed) ? data.feed : [];
            const articles = feed.map(item => {
                const publishedEpoch = item.time_published ? Math.floor(Date.parse(item.time_published.replace(/(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})/, '$1-$2-$3T$4:$5:$6Z')) / 1000) : 0;
                const ts = Array.isArray(item.ticker_sentiment) ? item.ticker_sentiment : [];
                const match = ts.find(t => t.ticker === symbol);

                return {
                    title: item.title || '',
                    summary: item.summary || '',
                    source: item.source || '',
                    url: item.url || '',
                    bannerImage: item.banner_image || '',
                    sentimentLabel: item.overall_sentiment_label || '',
                    sentimentScore: parseFloat(item.overall_sentiment_score) || null,
                    timePublished: publishedEpoch || null,
                    relevanceScore: match ? parseFloat(match.relevance_score) : null
                };
            });

            // CHECK NORMALIZED DATA FOR NULL METRICS
            const hasNulls = detectNullMetrics(articles);
            Debug.log('⚠️ Null metrics detected:', hasNulls);
            if (hasNulls) {
                Debug.warn('[WARNING] API fetch logic may need calibration: null sentiment/relevance values detected.');
                alert(`⚠️ Data Warning \n\nSome news items are missing sentiment or relevance data. \nCalculations will continue, but results may be incomplete. \n\nThis indicates API response variability and/or parsing logic mis-calibration. \n\nClick OK to continue.`);
            }

            // CREATE META DATA AND UPDATE ACTIVE NEWS RANGE
            const expiry = computeNewsExpiry(nowEpoch, fromEpoch, rangeUnit, rangeValue);
            const rangeKey = `${rangeUnit}_${rangeValue}`;
            activeNewsRange = rangeKey;
            Debug.log(`Feed expiry: ${expiry}`);
            Debug.log(`Range key: ${rangeKey}`);
            Debug.log(`Active news range: ${activeNewsRange}`);
            Debug.log(`Article count: ${articles.length}`);
            Debug.end();
            Debug.end();
            // RETURN NORMALIZED DATA
            return {
                range: rangeKey,
                expiry,
                articles
            };
        } catch (err) {
            const msg = String(err?.message || err).toLowerCase();
            if (msg.includes('rate limit') || msg.includes('api call frequency')) {
                Debug.log(`API key failed → ${apiKey}`);
                markKeyAsFailed(apiKey);
                attempts++;
                Debug.end();
                continue;
            }
            Debug.end();
            throw err;
        }
    }
    Debug.open(' [ ERROR: Fetch News ]');
    Debug.error('❌ All API keys exhausted');
    Debug.end();
    throw new Error('Fetch News: Unknown error.');
}
// ASYNC: FETCH ALPHA VANTAGE OVERVIEW
async function fetchAlphaVantageOverview(ticker) {
    Debug.group('[ FETCH OVERVIEW ]');

    Debug.subgroup('{ Input validation }');
    Debug.log('Input:', ticker);
    Debug.end();

    // VALIDATE INPUT PARAMETER(S)
    if (!ticker) {
        Debug.error('Ticker symbol required');
        Debug.end();
        Debug.end();
        throw new Error('Invalid ticker symbol');
    }

    // FETCH COMPANY OVERVIEW
    const symbol = String(ticker).trim().toUpperCase();
    let attempts = 0;
    const maxAttempts = API_KEYS.length;
    Debug.subgroup('{ Normalized input }');
    Debug.log('ticker:', symbol);
    Debug.log('maxAttempts:', maxAttempts);
    Debug.end();

    while (attempts < maxAttempts) {
        const apiKey = getNextApiKey();
        Debug.subgroup(`{ Attempt ${attempts + 1} }`);
        Debug.log('apiKey:', apiKey);

        // VALIDATE API KEY
        if (!apiKey) {
            Debug.open('[ ERROR: Fetch Overview ]');
            Debug.error('API key missing');
            Debug.end();
            break;
        }
        const url = `${ALPHA_VANTAGE_BASE_URL}function=OVERVIEW&symbol=${encodeURIComponent(ticker)}&apikey=${apiKey}`;
        Debug.log('url:', url);

        try {
            const response = await fetch(url);
            const data = await response.json();
            const apiError = data?.Note || data?.['Error Message'];

            // VERIFY API RESPONSE
            if (apiError) {
                Debug.warn('API error:', apiError);

                if (/api call frequency|rate limit|thank you/i.test(apiError)) {
                    Debug.log('rate limit → rotating key');
                    markKeyAsFailed(apiKey);
                    attempts++;
                    Debug.end();
                    continue;
                }
                Debug.end();
                throw new Error(apiError);
            }

            // VALIDATE RAW DATA
            if (!data || typeof data !== 'object' || !data.Name) {
                Debug.error('Malformed response');
                Debug.end();
                Debug.end();
                throw new Error('Malformed response');
            }
            Debug.log('NORMALIZED');
            Debug.end();
            Debug.end();

            // RETURN NORMALIZED TRIMMED DATA
            return {
                name: data.Name || '',
                exchange: data.Exchange || '',
                sector: data.Sector || '',
                industry: data.Industry || '',
                country: data.Country || '',
                website: data.OfficialSite || '',
                marketCap: Number(data.MarketCapitalization) || 0,
                weekHigh: Number(data['52WeekHigh']) || 0,
                weekLow: Number(data['52WeekLow']) || 0,
                target: Number(data.AnalystTargetPrice) || 0,
                ratings: {
                    strongBuy: Number(data.AnalystRatingStrongBuy) || 0,
                    buy: Number(data.AnalystRatingBuy) || 0,
                    hold: Number(data.AnalystRatingHold) || 0,
                    sell: Number(data.AnalystRatingSell) || 0,
                    strongSell: Number(data.AnalystRatingStrongSell) || 0
                },
                description: data.Description || ''
            };
        } catch (err) {
            const msg = String(err?.message || err).toLowerCase();
            if (msg.includes('rate limit') || msg.includes('api call frequency')) {
                Debug.log(`API key failed → ${apiKey}`);
                markKeyAsFailed(apiKey);
                attempts++;
                Debug.end();
                continue;
            }
            Debug.end();
            throw err;
        }
    }
    Debug.open('[ ERROR: Fetch Overview ]');
    Debug.error('All API keys exhausted');
    Debug.end();
    throw new Error('Fetch Overview: Unknown error.');
}
// ASYNC: FETCH ALPHA VANTAGE QUOTE
async function fetchAlphaVantageQuote(ticker) {
    Debug.group('[ FETCH QUOTE ]');

    Debug.subgroup('{ Input validation }');
    Debug.log('Input:', ticker);
    Debug.end();

    // VALIDATE INPUT PARAMETER(S)
    if (!ticker) {
        Debug.open('[ ERROR: Fetch Quote ]');
        Debug.error('Ticker symbol required.');
        Debug.end();
        Debug.end();
        throw new Error('Invalid ticker symbol.');
    }

    // FETCH GLOBAL QUOTE
    const symbol = String(ticker).trim().toUpperCase();
    let attempts = 0;
    const maxAttempts = API_KEYS.length;
    Debug.subgroup('{ Normalized input }');
    Debug.log('Ticker:', symbol);
    Debug.log('Max attempts:', maxAttempts);
    Debug.end();

    while (attempts < maxAttempts) {
        const apiKey = getNextApiKey();
        Debug.subgroup(`{ Attempt ${attempts + 1} }`);
        Debug.log('API Key:', apiKey);

        // VALIDATE API KEY
        if (!apiKey) {
            Debug.open('[ ERROR: Fetch Quote ]');
            Debug.error('API key: missing');
            Debug.end();
            break;
        }
        const url = `${ALPHA_VANTAGE_BASE_URL}function=GLOBAL_QUOTE&symbol=${encodeURIComponent(ticker)}&apikey=${apiKey}`;
        Debug.log('url:', url);
        try {
            const response = await fetch(url);
            const data = await response.json();
            const apiError = data?.Note || data?.['Error Message'];

            // VERIFY API RESPONSE
            if (apiError) {
                Debug.warn('API error:', apiError);
                if (/api call frequency|rate limit|thank you/i.test(apiError)) {
                    Debug.log('rate limit → rotating key');
                    markKeyAsFailed(apiKey);
                    attempts++;
                    Debug.end();
                    continue;
                }
                Debug.end();
                throw new Error(apiError);
            }
            const raw = data?.['Global Quote'];

            // VALIDATE RAW DATA
            if (!raw) {
                Debug.error('Malformed response');
                Debug.end();
                Debug.end();
                throw new Error('Malformed response');
            }

            // TRIM RAW DATA
            const rawSymbol = raw['01. symbol'];
            const rawPrice = raw['05. price'];
            const rawChange = raw['10. change percent'];
            Debug.subgroup('{ Raw data }');
            Debug.log(`Ticker symbol: ${rawSymbol}`);
            Debug.log(`Market price: ${rawPrice}`);
            Debug.log(`Percentage change: ${rawChange}`);
            Debug.end();

            // SYMBOL VERIFICATION
            if (!rawSymbol || rawSymbol.toUpperCase() !== symbol) {
                Debug.error('Ticker symbol verification: failed');
                Debug.log(`${rawSymbol} ≠ ${symbol}`);
                Debug.end();
                Debug.end();
                throw new Error(`Ticker symbol from raw data does not match user input. ${rawSymbol.toUpperCase()} != ${symbol}`);
            }

            // NORMALIZE RAW DATA
            const price = Number(rawPrice) || 0;
            const change = Number(String(rawChange || '').replace('%', '')) || 0;
            Debug.subgroup('{ Normalization }');
            Debug.log(`Market price: ${price}`);
            Debug.log(`Percentage change: ${change}`);
            Debug.end();

            Debug.log('NORMALIZED');
            Debug.end();
            Debug.end();
            return {
                price,
                change
            };
        } catch (err) {
            const msg = String(err?.message || err).toLowerCase();
            if (msg.includes('rate limit') || msg.includes('api call frequency')) {
                Debug.log(`API key failed → ${apiKey}`);
                markKeyAsFailed(apiKey);
                attempts++;
                Debug.end();
                continue;
            }
            Debug.end();
            throw err;
        }
    }
    Debug.open('[ ERROR: Fetch Quote ]');
    Debug.error('All API keys exhausted');
    Debug.end();
    throw new Error('Fetch Quote: Unknown error.');
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// C A L C U L A T I O N S |||||||||||||||||||||||||||||||||||
// FMS ROUND
function configureFMSRound(value, intervals, constraint = null) {
    Debug.log('Configuring FMS round...');

    // DETERMINE ROUNDING INTERVAL
    let step = intervals[intervals.length - 1].interval;
    for (let i = 0; i < intervals.length; i++) {
        if (value < intervals[i].limit) {
            step = intervals[i].interval;
            break;
        }
    }

    // VARIABLES
    const factor = 1 / step;
    const lower = Math.floor(value * factor) / factor;
    const upper = Math.ceil(value * factor) / factor;

    // EXACT HIT
    if (lower === upper) {
        Debug.log('FMSRound (Exact hit ✓✓✓):', lower);
        Debug.log('...configured FMS round:');
        return lower;
    }

    // CONSTRAINT-AWARE ROUNDING (SHARES)
    let rounded;
    if (constraint) {
        const {
            bidPrice,
            brokerageFee,
            minimumThreshold
        } = constraint;
        const feeMultiplier = 1 + brokerageFee;
        const lowerCost = lower * bidPrice * feeMultiplier;
        if (lowerCost < minimumThreshold) {
            rounded = upper;
        } else {
            const diffLower = value - lower;
            const diffUpper = upper - value;
            rounded = diffLower <= diffUpper ? lower : upper;
        }
    } else {
        const diffLower = value - lower;
        const diffUpper = upper - value;
        rounded = diffLower <= diffUpper ? lower : upper;
    }

    Debug.log(`FMSRound: ${rounded}`);
    Debug.log('...configured FMS round.');

    return rounded;
}
// CALCULATE FMS
function calculateFMS(quoteData, settings, market) {
    Debug.group('[ CALCULATE FMS ]');

    // VALIDATION
    if (!quoteData || typeof quoteData.price !== 'number') {
        Debug.open('« ERROR: Calculate FMS »');
        Debug,error('Invalid data');
        Debug.end();
        throw new Error('Invalid data');
    }
    if (!settings) {
        Debug.open('« ERROR: Calculate FMS »');
        Debug.error('Invalid settings');
        Debug.end();
        throw new Error('Invalid settings');
    }

    // VARIABLES: SETTINGS
    const price = quoteData.price;
    const discountPct = settings.activeDiscount / 100;
    const feePct = settings.activeFee / 100;
    const minPct = settings.activeMinimum / 100;
    const maxPct = settings.activeMaximum / 100;
    // VARIABKES: BID VALUES
    const rawBidPrice = price * (1 - discountPct);
    const bidPrice = fmsRound(rawBidPrice, PRICE_ROUNDING_INTERVALS);
    // VARIABLES: SELL VALUES
    const rawMinSell = bidPrice * (1 + minPct);
    const rawMaxSell = bidPrice * (1 + maxPct);
    const priceMinimum = fmsRound(rawMinSell, PRICE_ROUNDING_INTERVALS);
    const priceMaximum = fmsRound(rawMaxSell, PRICE_ROUNDING_INTERVALS);
    // VARIABLES: BLOCK SIZES
    const feeMultiplier = 1 + feePct;
    const rawBlockMin = DEFAULT_MINIMUM_THRESHOLD / (bidPrice * feeMultiplier);
    const blockMin = Math.max(1, configureFMSRound(rawBlockMin, SHARE_ROUNDING_INTERVALS, {
        bidPrice: bidPrice,
        brokerageFee: feePct,
        minimumThreshold: DEFAULT_MINIMUM_THRESHOLD
    }));
    const blockMinDouble = blockMin * 2;
    const blockMaxHalf = Math.ceil(blockMin / 2);
    const blockMax = Math.ceil(blockMin * 1.5);
    // FUNCTIONS: COST VALUES
    function buyCost(shares) {
        const base = shares * bidPrice;
        return base + (base * feePct);
    }
    function sellValue(shares, sellPrice) {
        const gross = shares * sellPrice;
        return gross - (gross * feePct);
    }
    // VARIABLES: COST VALUES
    const costMin = buyCost(blockMin);
    const costMinDouble = buyCost(blockMinDouble);
    const costMaxHalf = buyCost(blockMaxHalf);
    const costMax = buyCost(blockMax);
    // VARIABLES: SELL VALUES
    const sellMin = sellValue(blockMin, priceMinimum);
    const sellMinDouble = sellValue(blockMinDouble, priceMinimum);
    const sellMaxHalf = sellValue(blockMaxHalf, priceMaximum);
    const sellMax = sellValue(blockMax, priceMaximum);
    // VARIABLES: PROFIT VALUES
    const profitMin = sellMin - costMin;
    const profitMinDouble = sellMinDouble - costMinDouble;
    const profitMaxHalf = sellMaxHalf - costMaxHalf;
    const profitMax = sellMax - costMax;
    // VARIABLES: SERIAL NUMBER
    const serial = DateCache.metrics.generateSerial('TICKER', settings, marketState?.nextEventEpoch || 0);
    // VARIABLES: RAW METRICS
    const metricsRaw = {
        // BUY AND SELL VALUES
        priceBid: bidPrice,
        priceMinimum,
        priceMaximum,
        // PERCENTAGES
        percentDiscount: settings.activeDiscount,
        percentMinimum: settings.activeMinimum,
        percentMaximum: settings.activeMaximum,
        // BLOCK SIZES
        blockMin,
        blockMinDouble,
        blockMaxHalf,
        blockMax,
        // BASE COST VALUES
        costMin,
        costMinDouble,
        costMaxHalf,
        costMax,
        // COMMISSION VALUES
        commsMin: costMin - (blockMin * bidPrice),
        commsMinDouble: costMinDouble - (blockMinDouble * bidPrice),
        commsMaxHalf: costMaxHalf - (blockMaxHalf * bidPrice),
        commsMax: costMax - (blockMax * bidPrice),
        // TOTAL COST VALUES
        totalMin: costMin,
        totalMinDouble: costMinDouble,
        totalMaxHalf: costMaxHalf,
        totalMax: costMax,
        // SELL PRICE VALUES
        sellMin,
        sellMinDouble,
        sellMaxHalf,
        sellMax,
        // PROFIT AMOUNT VALUES
        profitMin,
        profitMinDouble,
        profitMaxHalf,
        profitMax,
        // UNIQUE TRADE SERIAL NUMBER
        serial
    };

    Debug.subgroup('< DATA: Metrics Raw >');
    Debug.log(`Metrics serial number: ${serial}`);
    Debug.log(`Metrics (raw): ${metricsRaw}`);
    Debug.end();

    Debug.log('...calculated FMS.');
    Debug.end();

    return {
        metricsRaw,
        serial
    };
}
// CALCULATE RATINGS
function calculateRatings(ratingsData) {
    Debug.group('[ CALCULATE RATINGS ]');

    // VALIDATION
    if (!ratingsData) {
        Debug.open('« ERROR: Calculate Ratings »');
        Debug.error('Invalid data');
        Debug.end();
        throw new Error('Invalid data');
    }

    // VARIABLES
    const {
        strongBuy = 0,
        buy = 0,
        hold = 0,
        sell = 0,
        strongSell = 0
    } = ratingsData;
    const total = strongBuy + buy + hold + sell + strongSell;

    // MISSING RATINGS DATA: SET SCORE TO NEUTRAL (50)
    if (total === 0) {
        Debug.open('‹ WARNING ›');
        Debug.warn('Analyst ratings data not available.');
        Debug.log('Score: 50');
        Debug.end();
        return {
            score: 50,
            label: 'No ratings data'
        };
    }

    // VARIABLES
    const weighted = (strongBuy * 100) + (buy * 75) + (hold * 50) + (sell * 25) + (strongSell * 0);
    const score = Math.round(weighted / total);
    let label;

    // DETERMINE SCORE LABEL
    if (score <= 20) label = 'Strong Sell';
    else if (score <= 40) label = 'Sell';
    else if (score <= 60) label = 'Hold';
    else if (score <= 80) label = 'Buy';
    else label = 'Strong Buy';

    Debug.subgroup('{ Analyst ratings }');
    Debug.log('Count:', total);
    Debug.log('Score:', score);
    Debug.log('Label:', label);
    Debug.end();
    Debug.end();

    return {
        score,
        label
    };
}
// CALCULATE 
function calculateTimezones(timestamp) {
    const msLAX = formatDateTime(timestamp, 'LAX');
    const msNYC = formatDateTime(timestamp, 'NYC');
    const UTC = formatDateTime(timestamp);
    const msLON = formatDateTime(timestamp, 'LON');
    const msPAR = formatDateTime(timestamp, 'PAR')
    const msJNB = formatDateTime(timestamp, 'JNB');
    const msMOW = formatDateTime(timestamp, 'MOW');
    const msDXB = formatDateTime(timestamp, 'DXB');
    const msHKG = formatDateTime(timestamp, 'HKG');
    const MNL = formatDateTime(timestamp, 'MNL');
    const msTYO = formatDateTime(timestamp, 'TYO');
    return { 
        LAX: msLAX, 
        NYC: msNYC, 
        UTC: UTC, 
        LON: msLON, 
        PAR: msPAR, 
        JNB: msJNB, 
        MOW: msMOW, 
        DXB: msDXB, 
        HKG: msHKG, 
        MNL: MNL, 
        TYO: msTYO 
    };
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// N E W S - F E E D |||||||||||||||||||||||||||||||||||||||||
// GLOBALS
let allNews = [];
let sortField = 'date';
let sortOrder = 'desc';
let lastWidth = window.innerWidth;
let sortAnimator;
let resizeTimeout;
const NEWS_RANGES = {
    DEFAULT: 'MONTH_1',
    getAllRanges: function() {
        const ranges = [];
        // Generate DAY_1 to DAY_6
        for (let i = 1; i <= 6; i++) ranges.push(`DAY_${i}`);
        // Generate WEEK_1 to WEEK_3
        for (let i = 1; i <= 3; i++) ranges.push(`WEEK_${i}`);
        // Generate MONTH_1 to MONTH_11
        for (let i = 1; i <= 11; i++) ranges.push(`MONTH_${i}`);
        // Generate YEAR_1 to YEAR_10
        for (let i = 1; i <= 10; i++) ranges.push(`YEAR_${i}`);
        return ranges;
    }
};
// CURATE NEWS FEED
function curateNewsFeed(newsData) {
    Debug.group('[ CURATE NEWS FEED ]');

    if (!newsData || !Array.isArray(newsData.articles)) {
        Debug.open('« ERROR »');
        Debug.error('Invalid news data.');
        Debug.end();
        throw new Error('Invalid news data.');
    }

    // PHASE 1: RELEVANCE COMPRESSION (SIGNAL EXTRACTION)
    let articles = newsData.articles.slice();
    const total = articles.length;
    let trimRatio;
    if (total <= 10) trimRatio = 1.0;
    else if (total <= 20) trimRatio = 0.75;
    else if (total <= 40) trimRatio = 0.5;
    else trimRatio = 0.35;
    const keepCount = Math.max(5, Math.floor(total * trimRatio));
    articles = articles.slice(0, keepCount); // Articles are relevance-sorted by API
    articles = articles.map(a => ({
        ...a,
        relevance: Math.pow(a.relevance, 1.15)
    })); // Optional soft relevance shaping (amplification, not reordering)
   
    Debug.subgroup(' \n< PHASE 1: Signal Extraction >\n ');
    Debug.log('Pre-compression phase:');
    Debug.log('    Count:', total);
    Debug.log('    Ratio:', trimRatio);
    Debug.log('Post-compression:');
    Debug.log(`    Count: ${keepCount}\n `);
    Debug.end();

    // PHASE 2: SENTIMENT AMPLIFICATION (VISUAL CLARITY)
    articles = articles.map(a => {
        let amplified = a.sentiment;
        if (amplified > 0) {
            amplified = Math.pow(amplified, 1.2);
        } else if (amplified < 0) {
            amplified = -Math.pow(Math.abs(amplified), 1.2);
        };
        return {
            ...a,
            sentiment: amplified
        };
    });

    Debug.subgroup(' \n< PHASE 2: Visual Clarity >\n ');
    Debug.log('Pre-amplification phase:');
    Debug.log('    Amplified:', amplified);
    Debug.log(`    Articles: ${articles}\n `);
    Debug.end();

    // PHASE 3A: DEFAULT SORTING (Primary sort: sentiment-weighted relevance)
    articles.sort((a, b) => {
        const scoreA = a.relevance * (1 + Math.abs(a.sentiment));
        const scoreB = b.relevance * (1 + Math.abs(b.sentiment));
        return scoreB - scoreA;
    });

    Debug.subgroup(' \n< PHASE 3A: Primary Sort >\n ');
    Debug.log('Pre-compression phase:');
    Debug.log('    A:', scoreA);
    Debug.log('    B:', scoreB);
    Debug.log(`    B - A: ${scoreB} - ${scoreA}\n `);
    Debug.end();

    // PHASE 3B: DEFAULT SORTING (Secondary stabilization: recency within close scores)
    articles.sort((a, b) => {
        const delta = Math.abs((b.relevance * (1 + Math.abs(b.sentiment))) - (a.relevance * (1 + Math.abs(a.sentiment))));
        if (delta < 0.05) {
            DeDebug.subgroup(' \n< PHASE 3B: Secondary Sort >\n ');
            Debug.log('    Delta:', delta);
            Debug.log('    A published:', a.published);
            Debug.log('    B published:', b.published);
            Debug.log(`    b - a: ${b.published} - ${a.published}\n `);
            Debug.end();

            Debug.end();
            return b.published - a.published;
        }
        Debug.end();
        return 0;
    });

    Debug.subgroup(' \n< Normalized >\n ');
    Debug.log('    Data range:',newsData.range);
    Debug.log(`    Articles: ${articles}\n `);
    Debug.end();

    Debug.end();
    return {
        range: newsData.range,
        articles
    };
}
// CREATE NEWS ITEM
function createNewsItem(article, pubDateStr, ageDays) {
    const dateDisplay = `${pubDateStr}${ageDays ? ` (${ageDays} days ago)` : ''}`;
    const sentiment = getSentimentInfo(article.sentimentScore || 0);
    const sentimentLabel = sentiment.label;
    const sentimentColor = sentiment.color;
    return `
        <!-- NEWS CARD -->
        <div class="news-card">

            <!-- NEWS CARD: SENTIMENT LAYER -->
            <div onclick="toggleNewsSummary(this.closest('.card-background'))" class="news-card--sentiment-layer"></div>

            <!-- NEWS CARD: CONTENT -->
            <div class="news-card--content">

                <!-- NEWS CARD CONTENT: TOP -->
                <div class="news-card--content-top">

                    <!-- NEWS CARD CONTENT TOP: CONTAINER -->
                    <div class="news-card--content-top--container">

                        <!-- NEWS CARD CONTENT TOP CONTAINER: LABEL -->
                        <div class="news-card--content-top--container-label">

                            <!-- NEWS CARD CONTENT TOP CONTAINER LABEL: BOX -->
                            <div class="news-card--content-top--container-label--box">Title</div>

                        </div>

                        <!-- SUMMARY -->
                        <div class="news-card--content-top--container-label">

                            <!-- NEWS CARD CONTENT TOP CONTAINER LABEL: BOX -->
                            <div class="news-card--content-top--container-label--box">Summary</div>

                        </div>

                    </div>

                    <!-- PUBLISHER -->
                    <div class="relative z-50    pointer-events-auto">
                        <a href="${article.url}" target="_blank" rel="noopener" class="text-value--link    publisher    bg-cnvscol rounded-l-lg    truncate whitespace-nowrap    -mr-2 pr-7 px-2 py-1">visit: ${article.source || 'Unknown'}</a>
                    </div>

                </div>
                
                <!-- MIDDLE - Expands in both directions -->
                <div class="middle-row    flex-1 flex items-center justify-center mt-1    font-light text-xs md:text-sm lg:text-base xl:text-lg    cursor-pointer    relative    transition-all duration-500 transform-gpu">

                    <!-- TITLE -->
                    <div class="title-content    w-full    px-4    absolute    opacity-100 transition-opacity duration-1000">
                        <p class="text-value font-light line-clamp-3">${article.title}</p>
                    </div>

                    <!-- SUMMARY -->
                    <div class="summary-content    w-full    px-4    absolute    opacity-0 transition-opacity duration-1000">
                        <p class="text-value font-light line-clamp-5">${article.summary || 'No summary available.'}</p>
                    </div>

                </div>

                <!-- BOTTOM - Will move DOWN when expanded -->
                <div class="bottom-row    flex flex-row justify-between items-center    mb-2    font-light text-xs md:text-sm lg:text-base    transition-all duration-1000 transform-gpu">

                    <!-- DATE -->
                    <span class="date text-label--mono    bg-cnvscol rounded-r-lg    truncate whitespace-nowrap    -ml-2 pl-7 px-2 py-1">${dateDisplay}</span>

                    <!-- SENTIMENT -->
                    <div class="text-label--mono    bg-cnvscol rounded-l-lg    truncate uppercase whitespace-nowrap    -mr-2 pr-7 px-2 py-1 ${sentimentColor}">${sentimentLabel}</div>

                </div>

            </div>

        </div>

    `;

}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// R E N D E R I N G |||||||||||||||||||||||||||||||||||||||||
// RENDER CALENDAR
function renderCalendar(market) {
    // VARABLES
    const data = DOM.overlay.data;
    const now = new Date();
    const phDateStr = formatDateTime(now, 'MNL', 'date');
    const etDateStr = formatDateTime(now, 'NYC', 'date');

    // INJECT DATA
    data.datePH.textContent = phDateStr;
    data.dateET.textContent = etDateStr;
    data.marketState.textContent = market.isOpen ? 'Open' : 'Closed';

    // DETERMINE HOLIDAY STATE
    let holidayName = '--';
    let holidayDate = 'YYYY-MM-DD';
    if (market.holidays?.next?.anchorEpoch) {
        const d = new Date(market.holidays.next.anchorEpoch * 1000);
        holidayName = market.holidays.next.name || '--';
        holidayDate = formatDateTime(d, 'NYC', 'date');
        /* holidayDate = d.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
        */
    }

    // INJECT DATA
    data.holidayName.textContent = holidayName;
    data.holidayDate.textContent = holidayDate;

    // DETERMINE MARKET STATE
    if (market.nextEvent?.epoch) {
        DateCache.countdown.countdown.start('market', market.nextEvent.epoch, ({ formatted, expired }) => { 
            data.marketCount.textContent = expired ? 'now' : formatted; 
        });
    }
    if (market.holidays?.next?.preClose) {
        DateCache.countdown.countdown.start('holiday', market.holidays.next.preClose, ({ formatted, expired }) => {
            data.holidayCount.textContent = expired ? 'now' : formatted;
        });
    }
}
// RENDER RATINGS INDICATOR
function renderRatingsIndicator(score) {
    Debug.log('Rendering ratings indicator...');

    // VALIDATION
    if (!wrapper || !label || !indicator) {
        Debug.open('« ERROR: »')
        Debug.error(`Element(s) missing, ${wrapper}, ${label}, ${indicator}`);
        return;
    }

    // VARIABLES
    const clamped = Math.max(0, Math.min(100, score));
    const data = DOM.motherboard.data;

    // RENDER INDICATOR
    data.indicatorWrapper.style.display = 'flex';
    data.indicatorWrapper.style.left = `${clamped}%`;
    data.indicatorWrapper.style.transform = 'translateX(-50%)';
    data.indicatorLabel.textContent = `${clamped}%`;
    data.indicatorLabel.classList.remove('opacity-0');
    data.indicator.classList.remove('opacity-0');

    // COMPUTE COLOR
    let color;
    if (clamped <= 25) color = 'red-500';
    else if (clamped <= 50) color = 'yellow-500';
    else if (clamped <= 75) color = 'lime-500';
    else color = 'green-500';

    // INJECT DATA
    data.indicatorLabel.className = `text-xs font-thin text-${color} opacity-75`;
    data.indicator.className = data.indicator.className.replace(/border-[tb]-\w+-500/g, '').trim();
    data.indicator.classList.add(`border-t-${color}`);

    Debug.log('...rendered ratings indicator.');
}
// RENDER TIMEZONES
function renderTimezones() {
    Debug.group('[ RENDER TIMEZONES ]');

    const timestamp = Date.now();

    Debug.log(' \nEpoch:', timestamp);
    Debug.log('Calculating timezones...');

    const timezones = calculateTimezones(timestamp);
    for (const [city, time] of Object.entries(timezones)) {
        Debug.log(`${city}:`, time);
    }

    Debug.log('...calculated timezones.\n ');
    Debug.end();
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// C L O C K |||||||||||||||||||||||||||||||||||||||||||||||||
// GLOBALS
const ClockUpdater = (() => {
    let timerId = null;
    function start() {
        stop();
        scheduleNext(0);
    }
    function stop() {
        if (timerId) {
            clearTimeout(timerId);
            timerId = null;
        }
    }
    function tick() {
        updateClocks();
        if (UI_STATE.OVERLAY.STATE.grabbing) {
            scheduleNext(250);
            return;
        }
        scheduleNext(resolveNextInterval());
    }
    function scheduleNext(ms) {
        timerId = setTimeout(tick, ms);
    }
    return { start, stop };
})();
// UPDATE CLOCKS
function updateClocks() {
    const data = DOM.overlay.data;
    const now = new Date();

    const phTimeMini = now.toLocaleTimeString('en-PH', {
        timeZone: 'Asia/Manila',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    const phTime = now.toLocaleTimeString('en-PH', {
        timeZone: 'Asia/Manila',
        hour12: false
    });
    const etTime = now.toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour12: false
    });

    data.timeDockedL.textContent = phTimeMini;
    data.timeDockedR.textContent = phTimeMini;
    data.timePH.textContent = phTime;
    data.timeET.textContent = etTime;
}
// RESOLVE NEXT INTERVAL
function resolveNextInterval() {
    Debug.subgroup('Resolving Next Interval...');

    if (UI_STATE.OVERLAY.STATE.docked) {
        Debug.log('Resolved next interval: 1 minute.');
        Debug.end();
        return 60_000;
    }

    Debug.log('Resolved next interval: seconds.');
    Debug.end();
    return 1_000;
}
// SYNC COUNTDOW
function syncCountdowns(market) {
    Debug.log('Synchronizing countdowns...');

    const data = DOM.overlay.data;
    if (market.nextEvent.epoch && market.nextEvent.epoch !== lastMarketEventEpoch) {
        lastMarketEventEpoch = market.nextEvent.epoch;
        DateCache.countdown.countdown.start('Next countdown (market):', market.nextEvent.epoch, ({
            formatted,
            expired
        }) => {
            data.marketCount.textContent = expired ? 'now' : formatted;
        });
    }
    if (market.holidays.next.preClose && market.holidays.next.preClose !== lastHolidayEpoch) {
        lastHolidayEpoch = market.holidays.next.preClose;
        DateCache.countdown.countdown.start('Next countdown (holiday):', market.holidays.next.preClose, ({
            formatted,
            expired
        }) => {
            data.holidayCount.textContent = expired ? 'now' : formatted;
        });
    }

    Debug.log('...synchronized Countdowns.');
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// A N I M A T I O N - E N G I N E |||||||||||||||||||||||||||
//GLOBALS
const HEIGHT_CACHE = {
    holidays: null
};
const REGISTRY = {
    MOTHERBOARD: [
        {
            sectionId: 'sectionMain',
            minimumIds: ['contentMain'],
            maximumIds: ['contentMain', 'contentInfo', 'contentMessage']
        },
        {
            sectionId: 'sectionInfo',
            minimumIds: [],
            maximumIds: ['contentInfo']
        },
        {
            sectionId: 'sectionMessage',
            minimumIds: [],
            maximumIds: ['contentMessage']
        },
        {
            sectionId: 'sectionDashboard',
            minimumIds: ['headDashboard'],
            maximumIds: ['headDashboard', 'contentDashboard']
        },
        {
            sectionId: 'sectionSettings',
            minimumIds: ['headSettings'],
            maximumIds: ['headSettings', 'contentSettings']
        },
        {
            sectionId: 'sectionOverview',
            minimumIds: ['headOverview'],
            maximumIds: ['headOverview', 'contentOverview']
        },
        {
            sectionId: 'sectionDescription',
            minimumIds: ['headDescription'],
            maximumIds: ['headDescription', 'contentDescription']
        },
        {
            sectionId: 'sectionRatings',
            minimumIds: ['headRatings'],
            maximumIds: ['headRatings', 'contentRatings']
        },
        {
            sectionId: 'sectionNews',
            minimumIds: ['headNews'],
            maximumIds: ['headNews', 'contentNews']
        }
    ],
    OVERLAY: [
        {
            sectionId: 'sectionToday',
            calculated: 'singleRow',
            minimumIds: [],
            maximumIds: ['contentToday']
        },
        {
            sectionId: 'sectionHoliday',
            minimumIds: [],
            maximumIds: ['contentHoliday']
        },
        {
            sectionId: 'sectionControl',
            minimumIds: [],
            maximumIds: ['contentControl']
        }
    ]
};
// MEASURE MIN HEIGHTS
function measureMinHeights() {
    Debug.log(' \nMeasuring motherboard minimum heights...');
    REGISTRY.MOTHERBOARD.forEach(({
        sectionId,
        minimumIds,
        calculated
    }) => {
        const S = DOM.motherboard.section[sectionId];
        if (!S) {
            Debug.open('« ERROR »');
            Debug.error(`Invalid section: ${sectionId}`);
            return;
        }

        const wasOpen = S.classList.contains('open');
        S.classList.add('open');

        let totalHeight = 0;

        if (calculated === 'singleRow') {
            const pad = 16;
            const row = 16;

            totalHeight = (pad * 2.5) + row;
        } else {
            minimumIds.forEach(minimumId => {
                const min = DOM.motherboard.content[minimumId];
                if (!min) {
                    Debug.open('« ERROR »');
                    Debug.error(`Invalid minimum id: ${minimumId}`);
                    Debug.end();
                    return;
                }

                totalHeight += min.scrollHeight;
            });
        }

        S.style.setProperty('--height-min', `${totalHeight}px`);

        Debug.subgroup(`< SECTION: Min-Height > → ${S.id}`);
        Debug.log(
            ` \nSection: ${sectionId}\n` +
            `Content : ${calculated === 'singleRow' ? 'CALCULATED' : totalHeight === 0 ? 'NO CONTENT' : minimumIds || 'calculated'}\n` +
            `Height : ${totalHeight}px\n`
        );
        Debug.end();

        if (!wasOpen) S.classList.remove('open');
    });
    Debug.log('...measured motherboard minimum heights.\n ');
}
// MEASURE MAX HEIGHTS
function measureMaxHeights() {
    Debug.log(' \nMeasuring motherboard maximum heights...');
    REGISTRY.MOTHERBOARD.forEach(({
        sectionId,
        maximumIds
    }) => {
        const S = DOM.motherboard.section[sectionId];
        if (!S) {
            Debug.open('« ERROR »');
            Debug.error(`Invalid section: ${sectionId}`);
            return;
        }

        const wasOpen = S.classList.contains('open');

        S.classList.add('open');

        let totalHeight = 0;

        maximumIds.forEach(maximumId => {
            const max = DOM.motherboard.content[maximumId];
            if (!max) {
                Debug.open('« ERROR »');
                Debug.error(`Invalid maximum id: ${maximumId}`);
                return;
            }
            totalHeight += max.scrollHeight;
        });
        S.style.setProperty('--height-max', `${totalHeight}px`);
        Debug.subgroup(`< SECTION: Max-Height > → ${S.id}`);
        Debug.log(` \nSection: ${sectionId}\n` +
            `Content: ${maximumIds}\n ` +
            `Height : ${totalHeight}px\n`);
        Debug.end();

        if (!wasOpen) S.classList.remove('open');
    });
    Debug.log('...measured motherboard maximum heights.\n ');
}
// MEASURE MAX DYNAMIC
function measureMaxDynamic(sectionId) {
    Debug.log('Measuring maximum height (dynamic)...');

    const section = document.getElementById(sectionId);
    if (!section) {
        Debug.open('« ERROR »');
        Debug.error('Invalid section:', section.id);
        return;
    }

    content = section.querySelector(':scope > *');
    if (!content) {
        Debug.open('[ ERROR: Measure max dynamic ]');
        Debug.error('Invalid content:', content.id);
        return;
    }

    content.offsetHeight;
    const height = content.scrollHeight;
    section.style.setProperty('--height-max', `${height}px`);

    Debug.log('...measured maximum height (dynamic).');
}
// MEASURE MIN HEIGHTS OVERLAY
function measureMinHeightsOverlay() {
    Debug.log(' \nMeasuring overlay minimum heights...');
    REGISTRY.OVERLAY.forEach(({
        sectionId,
        minimumIds,
        calculated
    }) => {
        const S = DOM.overlay.section[sectionId];
        if (!S) {
            Debug.open('« ERROR »');
            Debug.error(`Invalid section: ${sectionId}`);
            return;
        }

        const wasOpen = S.classList.contains('open');

        S.classList.add('open');

        let totalHeight = 0;

        if (calculated === 'singleRow') {
            const pad = 16;
            const row = 16;

            totalHeight = (pad * 2.5) + row;
        } else {
            minimumIds.forEach(minimumId => {
                const el = DOM.overlay.content[minimumId];
                if (!el) {
                    Debug.open('« ERROR »');
                    Debug.error(`Invalid minimum id: ${minimumId}`);
                    return;
                }

                totalHeight += el.scrollHeight;
            });
        }
        S.style.setProperty('--height-min', `${totalHeight}px`);
        Debug.subgroup(`< SECTION: Min-Height > → ${S.id}`);
        Debug.log(` \nSection: ${sectionId}\n` +
            `Content: ${calculated === 'singleRow' ? 'CALCULATED' : totalHeight === 0 ? 'NO CONTENT' : minimumIds}\n` +
            `Height : ${totalHeight}px\n`);
        Debug.end();

        if (!wasOpen) S.classList.remove('open');
    });
    Debug.log('...measured overlay minimum heights.\n ');
}
// MEASURE MAX HEIGHTS OVERLAY
function measureMaxHeightsOverlay() {
    Debug.log(' \nMeasuring overlay maximum heights...');
    REGISTRY.OVERLAY.forEach(({
        sectionId,
        maximumIds
    }) => {
        const S = DOM.overlay.section[sectionId];
        if (!S) {
            Debug.open('« ERROR »');
            Debug.error(`Invalid section: ${sectionId}`);
            return;
        }

        const wasOpen = S.classList.contains('open');
        S.classList.add('open');
        let totalHeight = 0;
        maximumIds.forEach(maximumId => {
            const el = DOM.overlay.content[maximumId];
            if (!el) {
                Debug.open('« ERROR »');
                Debug.error(`Invalid maximum id: ${maximumId}`);
                return;
            }
            totalHeight += el.scrollHeight;
        });
        S.style.setProperty('--height-max', `${totalHeight}px`);
        Debug.subgroup(`< SECTION: Max-Height > → ${S.id}`);
        Debug.log(` \nSection: ${sectionId}\n` +
            `Content: ${maximumIds}\n ` +
            `Height : ${totalHeight}px\n`);
        Debug.end();

        if (!wasOpen) S.classList.remove('open');
    });
    Debug.log('...measured overlay maximum heights.\n ');
}
// MEASURE ANIMATIONS
function measureAnimations() {
    Debug.group('[ MEASURE ANIMATIONS ]');

    Debug.subgroup('{ Overlay }');
    Debug.subgroup('{ Minimum Heights }');
    measureMinHeightsOverlay();
    Debug.end();
    Debug.subgroup('{ Maximum Heights }');
    measureMaxHeightsOverlay();
    Debug.end();
    Debug.end();
    Debug.subgroup('{ Motherboard }');
    Debug.subgroup('{ Minimum Heights }');
    measureMinHeights();
    Debug.end();
    Debug.subgroup('{ Maximum Heights }');
    measureMaxHeights();
    Debug.end();
    Debug.end();

    Debug.end();
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// S T A T E |||||||||||||||||||||||||||||||||||||||||||||||||
// GLOBALS
const ANIMATION_TIMING = {
    // STYLE TIMERS
    sectionOpen: 750,
    contentIn: 250,
    autoFade: 5000,
    // DURATION TIMERS
    t5000: 5000,
    t3000: 3000,
    t1000: 1000,
    t875: 875,
    t750: 750,
    t500: 500,
    t250: 250,
    t125: 125,
    // DELAY TIMERS
    d3000: 3000,
    d1000: 1000,
    d875: 875,
    d750: 750,
    d500: 500,
    d250: 250,
    d125: 125
};
const UI_STATE = {
    OVERLAY: {
        // OVERLAY LEVEL STATE
        CONSTANTS: {
            THRESHOLDS: {
                undock: 0.5,
                predock: 0.375
            },
            VISIBLE: {
                docked: 0.175
            }
        },
        EXECUTION: {
            locked: false,
            pending: false
        },
        STATE: {
            dblLock: false,
            docked: true,
            grabbing: false,
            predocked: false,
            side: 'right'
        },
        // MODULE LEVEL STATE
        MODULES: {
            CALENDAR: {
                CLASS: {
                    STATES: ['docked', 'undocked', 'predocked'],
                    MODIFIERS: ['grabbing']
                },
                LAYOUT: {
                    dockY: null,
                    posY: '5svh'
                },
                TOGGLE: {
                    holidays: false,
                    timezone: 'PH'
                }
            }
        }
    }
};
// GET DOCK SIDE
function getDockSide(el) {
    const rect = el.getBoundingClientRect();
    const vw = window.innerWidth;
    const hiddenLeft = Math.max(0, -rect.left);
    const hiddenRight = Math.max(0, rect.right - vw);
    const side = hiddenLeft > hiddenRight ? 'left' : 'right';
    return side;
}
// GET VISIBLE RATIO
function getVisibleRatio(el) {
    const rect = el.getBoundingClientRect();
    const vw = window.innerWidth;
    const visibleWidth = Math.max(0, Math.min(rect.right, vw) - Math.max(rect.left, 0));
    return visibleWidth / rect.width;
}
// RESOLVE OVERLAY CLASS
function resolveOverlayClass(el) {
    Debug.log(' \nResolving overlay class...');

    // VARIABLES
    const d = UI_STATE.OVERLAY.STATE.docked === true;
    const p = UI_STATE.OVERLAY.CONSTANTS.THRESHOLDS.predock;
    const ratio = getVisibleRatio(el);

    // RESOLVE CLASS
    let state = '';
    if (d) {
        state = 'docked';
    } else if (ratio <= p) {
        state = 'predocked';
    } else {
        state = 'undocked';
    }

    Debug.subgroup('{ Resolved Class }');
    Debug.log(' \nElement:', el.id, '\nClass:', state, '\n ');
    Debug.end();
    Debug.log('...resolved overlay class.\n ');
    return state;
}
// APPLY OVERLAY CLASS
async function applyOverlayClass(el, caller = '', klass, fast = false) {
    Debug.log(' \nApplying overlay class...');
    Debug.subgroup('< Overlay Report >');

    // VARIABLES
    const _S = UI_STATE.OVERLAY.MODULES.CALENDAR.CLASS.STATES;
    const d = UI_STATE.OVERLAY.STATE.docked;
    const g = UI_STATE.OVERLAY.STATE.grabbing;
    const t5k = ANIMATION_TIMING.t5000;

    // REMOVE PREVIOUS STATE CLASSES
    _S.forEach(s => el.classList.remove(s));

    // APPLY FAST CLASS
    if (fast) {
        Debug.log(' \nAdded fast class modifier.\n ');
        el.classList.add('fast');
    } else {
        Debug.log(' \nRemoved fast class modifier.\n ');
        el.classList.remove('fast');
    }

    // APPLY NEW STATE CLASS
    el.classList.add(klass);

    // APPLY OR SCHEDULE MODIFIER REMOVAL
    if (g) {
        el.classList.add('grabbing');
    } else if (d) {
        setTimeout(() => el.classList.remove('grabbing'), t5k);
    } else {
        el.classList.remove('grabbing');
    }

    // ASYNC FUNCTION LOG REPORT
    Debug.log(' \nCSS Class:', klass, '\nModifier:', g ? 'grabbing' : 'none', '\n ');
    Debug.end();
    Debug.log('...applied overlay class.\n ');

    // AWAIT TRANSITION
    const transition = await waitForTransition(el, caller);

    Debug.subgroup(`< Transition Report > → ${transition.caller}`);
    Debug.log(' \nElement:', transition.element, '\nDuration:', transition.duration, '\nDelay:', transition.delay, '\nTotal:', transition.total, '\nEnded by event:', transition.endedByEvent, '\nReason:', transition.endedByEvent === true ? 'event' : transition.reason, '\n ');
    Debug.end();
}
// APPLY DOCKED POSITION
function applyDockedPosition(side) {
    Debug.log(' \nApplying docked position...');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const D = DOM.overlay.data;
    const _V = UI_STATE.OVERLAY.CONSTANTS.VISIBLE;
    const _L = UI_STATE.OVERLAY.MODULES.CALENDAR.LAYOUT;

    //  GET ELEMENT DIMENTIONS, CALCULATE & APPLY DOCKED POSITION
    const rect = el.getBoundingClientRect();
    const hidden = rect.width * (1 - _V.docked);
    el.style.top = _L.dockY ?? '5svh';
    el.style.bottom = 'auto';

    // APPLY RELEVANT CLASS TO ROW ZERO ELEMENT BASED ON DOCK SIDE
    if (side === 'right') {
        el.style.right = `-${hidden}px`;
        el.style.left = 'auto';
        D.timeDockedL.classList.remove('out');
        D.timeDockedR.classList.add('out');
    } else {
        el.style.left = `-${hidden}px`;
        el.style.right = 'auto';
        D.timeDockedR.classList.remove('out');
        D.timeDockedL.classList.add('out');
    }

    Debug.subgroup('{ Docked Position }');
    Debug.log(' \nElement:', el.id, '\nDock side:', side, '\n ');
    Debug.end();
    Debug.log('...applied docked position.\n ');
}
// APPLY UNDOCKED POSITION
function applyUndockedPosition(el) {
    Debug.log('Applying undocked position...');

    // GET ELEMENT DIMENTIONS, CALCULATE & APPLY UNDOCKED POSITION
    const rect = el.getBoundingClientRect();
    const vw = window.innerWidth;
    el.style.inset = 'auto';
    el.style.left = `${Math.round((vw - rect.width) / 2)}px`;
    el.style.right = 'auto';
    el.style.bottom = 'auto';
    el.style.transform = 'none';
    const maxTop = window.innerHeight - rect.height;
    el.style.top = `${Math.max(0, Math.min(rect.top, maxTop))}px`;

    Debug.log('Element:', el.id);
    Debug.log('...applied undocked position.\n ');
}
// APPLY DOCKED STATE
async function applyDockedState(caller = '', fast = false) {
    Debug.log(' \nApplying docked state...');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.MODULES.CALENDAR.TOGGLE;
    const delay = fast === true ? 50 : 250;

    // MUTATE STATE
    _S.docked = true;
    _S.grabbing = false;

    // PREDOCKED BRANCH
    if (_S.predocked) {
        Debug.log(' \nFinishing predocked → docked...');

        hideContent(C.contentRowOnePH, `${caller} -h rowOnePH`, undefined, 1000, fast);
        showContent(C.contentRowZero, `${caller} -s rowZero`, undefined, 1050, fast);

        Debug.log('...finished predocked → docked.\n ')
    } else {
        Debug.log(' \nFull docked collapsing...');

        // TIMEZONE RESET
        if (_T.timezone === 'ET') {
            Debug.log('Reset timezones.');
            toggleTimezone(caller, fast);
        }

        // CLOSE CONTROL SECTION
        await hideContent(C.contentControl, `${caller} -h contentControls`, undefined, undefined, fast);
        await closeSection('sectionControl', `${caller} -c sectionControls`, undefined, undefined, fast);

        // CLOSE HOLIDAY SECTION
        if (_T.holidays) {
            Debug.log(' \nClosed Holiday section.');
            await toggleHolidays(caller, fast);
        }

        // CLOSE TODAY SECTION
        await hideContent(C.contentRowFour, `${caller} -h rowFour`, undefined, undefined, fast);
        unmorphSection('sectionToday', `${caller} -u sectionToday`, undefined, delay, fast);
        closeSection('sectionToday', `${caller} -c sectionToday`, undefined, undefined, fast);
        await hideContent(C.contentRowThree, `${caller} -h rowThree`, undefined, undefined, fast);
        await hideContent(C.contentRowTwoPH, `${caller} -h rowTwoPH`, undefined, undefined, fast);

        // SWITCH ROW ZERO
        hideContent(C.contentRowOnePH, `${caller} -h rowOnePH`, undefined, undefined, fast);
        showContent(C.contentRowZero, `${caller} -s rowZero`, undefined, delay / 5, fast);

        Debug.log('...full docked collapsed.\n ');
    }

    // RESET PREDOCKED STATE FLAG
    _S.predocked = false;

    Debug.log('...applied docked state.\n ');
}
// APPLY PREDOCKED STATE
async function applyPredockedState(caller = '') {
    Debug.log('Applying predocked state...');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.MODULES.CALENDAR.TOGGLE;
    const today = DOM.overlay.section.sectionToday;
    const anim = ANIMATION_TIMING;
    const fast = true;

    // RESER TIMEZONE ROWS
    if (_T.timezone === 'ET') {
        Debug.log('Reset timezones.');
        toggleTimezone(caller, fast);
    }

    // CLOSE CONTROLS SECTION
    await hideContent(C.contentControl, `${caller} -h contentControls`, undefined, undefined, fast);
    await closeSection('sectionControl', `${caller} -c sectionControls`, undefined, undefined, fast);

    // CLOSE HOLIDAYS SECTION
    if (_T.holidays) {
        Debug.log('Close holidays section.')
        await toggleHolidays(caller, fast);
    }

    // CLOSE TODAY SECTION
    unmorphSection('sectionToday', `${caller} -u sectionToday`, undefined, 25, fast);
    await hideContent(C.contentRowFour, `${caller} -h rowFour`, undefined, undefined, fast);
    closeSection('sectionToday', `${caller} -c sectionToday`, undefined, undefined, fast);
    await hideContent(C.contentRowThree, `${caller} -h rowThree`, undefined, undefined, fast);
    hideContent(C.contentRowTwoPH, `${caller} -h rowTwoPH`, undefined, undefined, fast);

    Debug.log('...applied predocked state.');
}
// APPLY UNDOCKED STATE
async function applyUndockedState(caller = '') {
    Debug.log(' \nApplying undocked state...');
    Debug.subgroup('{ Undocked State }');
    Debug.log('\n');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const _S = UI_STATE.OVERLAY.STATE;
    const today = DOM.overlay.section.sectionToday;

    // MUTATE OVERLAY STATE
    _S.docked = false;
    _S.grabbing = false;

    // APPLY UNDOCKED CLASSES
    morphSection('sectionToday', `${caller} -m sectionToday`, 'tl-b0', 250, undefined);
    openSection('sectionToday', `${caller} -o sectionToday`, undefined, undefined, undefined);
    await showContent(C.contentRowTwoPH, `${caller} -s rowTwoPH`, undefined, undefined, undefined);
    await showContent(C.contentRowThree, `${caller} -s rowThree`, undefined, undefined, undefined);
    await showContent(C.contentRowFour, `${caller} -s rowFour`, undefined, undefined, undefined);
    await openSection('sectionControl', `${caller} -o sectionControls`, undefined, undefined, undefined);
    await showContent(C.contentControl, `${caller} -s contentControls`, undefined, undefined, undefined);

    Debug.log('\n');
    Debug.end();
    Debug.log('...applied undocked state.\n ');
}
// APPLY INITIAL STATE
function applyInitialState() {
    Debug.group('[ APPLY INITIAL STATE ]');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const _S = UI_STATE.OVERLAY.STATE;
    const rowZero = DOM.overlay.content.contentRowZero;

    // SET INITIAL STATE
    _S.docked = true;
    _S.grabbing = false;

    // SET INITIAL POSITION
    applyDockedPosition('right');

    // SET INITIAL CLASSES & FADE IN OVERLAY
    rowZero.classList.add('in');
    el.classList.add('docked');
    el.classList.remove('out');

    Debug.end();
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// A N I M A T I O N S |||||||||||||||||||||||||||||||||||||||
// ASYNC: ANIMATE
async function animate(target, { caller = '', action = 'add', klass = 'open', kind = 'section', delay = 0, fast = false, } = {}) {
    // VALIDATION GUARD
    const el = typeof target === 'string' ? document.getElementById(target) : target;

    // RESET OFFSET
    el.offsetHeight;

    // CHECK DELAY PARAMETER & AWSIT IF EXISTS
    if (Number.isFinite(delay) && delay > 0) {
        Debug.log('Animate delay:', delay, 'ms');
        await wait(delay);
    }

    // CHECK FAST PARAMETER & APPKY IF TRUE
    if (fast) {
        el.classList.add('fast');
        Debug.log('Fast:', fast, '\nFast class added.\n ');
    }

    // APPLY ACTION TO CLASS & AWAIT TRANSITION
    el.classList[action](klass);

    // AWAIT TRANSITION
    const transition = await waitForTransition(el, caller);

    el.classList.remove('fast');

    // LOG TRANSITION
    Debug.subgroup(`< Transition Report > → ${transition.caller}`);
    Debug.log(' \nElement:', transition.element, '\nDuration:', transition.duration, 'ms', '\nDelay:', transition.delay, 'ms', '\nTotal:', transition.total, 'ms', '\nEnded by event:', transition.endedByEvent, '\nReason:', transition.endedByEvent === true ? 'event' : transition.reason, '\n ');
    Debug.end();

    // LOG ANIMATION
    Debug.subgroup(`< Animation Report > → ${el.id}`);
    Debug.log('\nElement:', el.id, '\nKind:', kind, '\nClass:', klass, '\nAction:', action, '\nFast:', fast, '\n ');
    Debug.end();
}
// ANIMATE HELPERS
const showContent  = (el, caller = '', klass = 'in', delay = 0, fast = false) => animate(el, { kind: 'content', action: 'add', caller, klass, delay, fast });
const hideContent  = (el, caller = '', klass = 'in', delay = 0, fast = false) => animate(el, { kind: 'content', action: 'remove', caller, klass, delay, fast });
const openSection  = (id, caller = '', klass = 'open', delay = 0, fast = false) => animate(id, { kind: 'section', action: 'add', caller, klass, delay, fast });
const closeSection = (id, caller = '', klass = 'open', delay = 0, fast = false) => animate(id, { kind: 'section', action: 'remove', caller, klass, delay, fast });
const morphSection = (id, caller = '', klass = 'tl-b0', delay = 0, fast = false) => animate(id, { kind: 'section', action: 'add', caller, klass, delay, fast });
const unmorphSection = (id, caller = '', klass = 'tl-b0', delay = 0, fast = false) => animate(id, { kind: 'section', action: 'remove', caller, klass, delay, fast });
///////////////////////////////// F U N C T I O N S |||||||||||||
///// U I - D R A G |||||||||||||||||||||||||||||||||||||||||||||
// GLOBALS
let startX, startY;
let startLeft, startTop;
let lastTerritory = null;
let lastClickTime = 0;
// POINTER DOWNb
function onPointerDown(e) {
    Debug.log(' \n[ON] POINTER DOWN\n------------------\n');
    Debug.group('[ POINTER DOWN ]');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const _S = UI_STATE.OVERLAY.STATE;
    const now = Date.now();
    const doubleClick = now - lastClickTime < 250;

    // DOUBLE CLICK OVERRIDE BRANCH
    lastClickTime = now;
    if (doubleClick) {
        Debug.log(' \nDouble click detected.\n Double click locked.');
        _S.dblLock = true;
        Debug.end();
        Debug.log('------------------\nPOINTER DOWN [OFF]\n ');
        onDoubleClick();
        Debug.end();
        return;
    }

    // VERIFICATION
    if (!el) {
        Debug.open('« ERROR »');
        Debug.error('Invalid element');
        Debug.end();
        return;
    }
    if (e.target.closest('button, input, select, textarea')) {
        Debug.log('Target is button.');
        Debug.end();
        Debug.log('------------------\nPOINTER DOWN [OFF]\n ');
        return;
    }

    // RESET LAST TERRITORY & FAST
    let lastTerritory = null;

    // ESTABLISH POINTER CAPTURE & GEOMETRY SNAPSHOT
    el.setPointerCapture(e.pointerId);
    const rect = el.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    startLeft = rect.left;
    startTop = rect.top;

    // MUTATE STATE & APPLY CLASS
    _S.grabbing = true;
    const klass = resolveOverlayClass(el);
    applyOverlayClass(el, 'pointer down', klass);

    // ATTACH MOVE/UP LISTENERS
    el.addEventListener('pointermove', onPointerMove);
    el.addEventListener('pointerup', onPointerUp);
    el.addEventListener('pointercancel', onPointerUp);

    Debug.log(' \nElement:', el.id, '\nDocked:', _S.docked, '\nGrabbing:', _S.grabbing, '\n ');
    Debug.end();
    Debug.log('------------------\nPOINTER DOWN [OFF]\n ');
}
// POINTER MOVE
function onPointerMove(e) {
    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.CONSTANTS.THRESHOLDS;

    // SET DOCK COORDINATES
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    // UPDATE POSITION
    el.style.left = `${startLeft + dx}px`;
    el.style.top = `${startTop + dy}px`;
    el.style.right = 'auto';
    el.style.bottom = 'auto';

    // CALCULATE RATIO AFTER POSITION UPDATE
    const ratio = getVisibleRatio(el);

    // UNDOCK THRESHOLD CROSSED: docked → undocked
    if (_S.docked && ratio >= _T.undock) {
        Debug.log('\n[ON] POINTER MOVE\n------------------\n');
        Debug.group('[ POINTER MOVE ]');

        // DETATCH MOVE/UP LISTENERS & RELEASE POINTER CLEANUP
        el.removeEventListener('pointerup', onPointerUp);
        el.removeEventListener('pointercancel', onPointerUp);
        el.removeEventListener('pointermove', onPointerMove);
        if (el.hasPointerCapture(e.pointerId)) {
            el.releasePointerCapture(e.pointerId);
        }

        // VARIABLES
        const C = DOM.overlay.content;

        // MUTATE STATE
        _S.docked = false;
        _S.grabbing = false;

        // HARD SWAP OVERLAY CLASSES
        el.classList.remove('docked', 'grabbing', 'fast');
        el.classList.add('undocked');
        C.contentRowZero.classList.remove('in');
        setTimeout(() => {
            C.contentRowOnePH.classList.add('in');
        }, 50);

        Debug.log(' \nDocked:', _S.docked, '\nGrabbing:', _S.grabbing, '\nPredocked:', _S.predocked, '\n ');
        Debug.end();
        Debug.log('------------------\nPOINTER MOVE [OFF]\n ');

        // APPLY UNDOCKED POSITION & STATE
        applyUndockedPosition(el);
        applyUndockedState('pointer move');

        return;
    }

    // UNDOCKED STATE: undocked ←→ predocked
    if (!_S.docked) {
        // VARIABLES
        const territory = ratio <= _T.predock ? 'dock' : 'undock';

        // APPLY FAST MODIFIER

        // TERRITORY CHANGE BRANCH
        if (territory !== lastTerritory) {
            Debug.log('\n[ON] POINTER MOVE\n------------------\n');
            Debug.group('[ POINTER MOVE ]');

            // UPDATE TERRITORY
            lastTerritory = territory;

            // TERRITORY CROSSED INTO DOCK ZONE
            if (territory === 'dock') {
                Debug.log('\nEntered dock territory.');

                // RESOLVE & APPLY OVERLAY CLASS
                const klass = resolveOverlayClass(el);
                applyOverlayClass(el, 'pointer move', klass);

                // RESET TIMER
                if (!_S.timer) {
                    Debug.log('Starting predock timer.');
                    _S.timer = setTimeout(() => {
                        if (lastTerritory === 'dock') {
                            _S.predocked = true;
                            applyPredockedState('pointer move');
                        }
                        _S.timer = null;
                    }, 3000);
                }
            } else {
                Debug.log('\nEntered undock territory.');

                // RESOLVE & APPLY OVERLAY CLASS
                const klass = resolveOverlayClass(el);
                applyOverlayClass(el, 'pointer move', klass);

                // CANCEL PREDOCKED TIMER
                if (_S.timer) {
                    clearTimeout(_S.timer);
                    _S.timer = null;

                    Debug.log('Cancelled predocked timer.');
                }
            }

            Debug.log(' \nDocked:', _S.docked, '\nGrabbing:', _S.grabbing, '\nPredocked:', _S.predocked, '\nTerritory:', territory, '\n ');
            Debug.end();
            Debug.log('------------------\nPOINTER MOVE [OFF]\n ');
        }
    }
}
// POINTER UP
function onPointerUp(e) {
    Debug.log('\n[ON] POINTER UP\n------------------');
    Debug.group('[ POINTER UP ]');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const c = DOM.overlay.section.sectionControl;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.CONSTANTS.THRESHOLDS;
    const _L = UI_STATE.OVERLAY.MODULES.CALENDAR.LAYOUT;

    // GUARD
    if (_S.dblLock) {
        Debug.log(' \nOn pointer up supressed.\nDouble click unlocked.');
        _S.dblLock = false;
        Debug.end();
        Debug.log('------------------\n  POINTER UP [OFF]\n ');
        return;
    }

    // DETATCH MOVE/UP LISTENERS & RELEASE POINTER CLEANUP
    el.removeEventListener('pointermove', onPointerMove);
    el.removeEventListener('pointerup', onPointerUp);
    el.removeEventListener('pointercancel', onPointerUp);
    if (el.hasPointerCapture(e.pointerId)) {
        el.releasePointerCapture(e.pointerId);
    }

    // CANCEL PENDING PREDOCK TIMER
    if (_S.timer) {
        Debug.log(' \nTimer cleared.');
        clearTimeout(_S.timer);
        _S.timer = null;
    }

    // REMOVE FAST CLASS OVERRIDE
    el.classList.remove('fast');

    // MUTATE STATE
    _S.grabbing = false;

    // RECHECK TERRITORY AT RELEASE
    const ratio = getVisibleRatio(el);
    const inPredockBranch = (_S.docked === false && ratio <= _T.predock);
    const inReundockBranch= (_S.docked === false && ratio > _T.predock);
    const inRedockBranch= (_S.docked === true && ratio <= _T.undock);

    // PREDOCK BRANCH
    if (inPredockBranch) {
        Debug.log(' \nStart of predock branch...');

        // CALCULATE Y-AXIS POSITION
        _L.dockY = el.style.top;

        // DETERMINE SIDE, APPLY DOCKED POSITION & STATE
        const side = getDockSide(el);
        applyDockedPosition(side);
        applyDockedState('pointer up');

        // MUTATE STATE
        _S.predocked = false;
        _S.docked = true;

        Debug.log('...end of predock branch.');
    } else if (inReundockBranch) {
        Debug.log(' \nStart of reundock branch...');

        // PREDOCKED STATE: TRUE
        if (_S.predocked) {
            Debug.log('Element predocked.');
            applyUndockedState('pointer up');
            _S.predocked = false;
        }

        Debug.log('...end of reundock branch.');
    } else if (inRedockBranch) {
        // REDOCK BRANCH
        Debug.log(' \nStart of redock branch...');

        // CALCULATE Y-AXIS POSITI9N
        _L.dockY = el.style.top;

        // DETERMINE DOCK SIDE & APPLY DOCKED POSITION
        const side = getDockSide(el);
        applyDockedPosition(side);

        Debug.log('...end of redock branch.');
    } else {
        Debug.log(' \nStart of undock branch...');

        // MUTATE STATE
        _S.docked = false;

        // HARD SWAP OVERLAY CLASSES
        el.classList.remove('docked', 'grabbing', 'fast');
        el.classList.add('undocked');
        C.contentRowZero.classList.remove('in');
        setTimeout(() => {
            C.contentRowOnePH.classList.add('in');
        }, 50);
        
    }

    // APPLY CLASS LAST
    const klass = resolveOverlayClass(el);
    applyOverlayClass(el, 'pointer up', klass);

    Debug.log('\nDocked:', _S.docked, '\nPredocked:', _S.predocked, '\n ');
    Debug.end();
    Debug.log('------------------\n  POINTER UP [OFF]\n ');
}
// DOUBLE CLICK
async function onDoubleClick(e) {
    Debug.log('\n[ON] DOUBLE CLICK\n------------------');
    Debug.group('[ DOUBLE CLICK ]');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const _S = UI_STATE.OVERLAY.STATE;
    const fast = true;

    // VERIFICATION
    if (_S.docked) return;

    // CANCEL PENDING PREDOCK TIMER
    if (_S.timer) {
        Debug.log(' \nTimer cancelled.');
        clearTimeout(_S.timer);
        _S.timer = null;
    }

    // APPLY DOCK POSITION & STATE
    applyDockedPosition('right');
    await applyDockedState('user double click', fast);

    // MUTATE STATE
    _S.docked = true;

    // RESOLVE & APPLY OVERLAY CLASA
    const klass = resolveOverlayClass(el);
    applyOverlayClass(el, 'user double click', klass, fast);

    // MUTATE STATE
    _S.dblLock = false;
    el.classList.remove('fast');

    Debug.log('\nDocked:', _S.docked, '\nPredocked:', _S.predocked, '\n ');
    Debug.end();
    Debug.log('------------------\n  DOUBLE CLICK [OFF]\n ');
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// U I - T O G G L E |||||||||||||||||||||||||||||||||||||||||
// ASYNC: TOGGLE DATA STATE
async function toggleDataState(toggle, caller, type = null, fast = false) {
    Debug.log(' \nToggle data state...');
    Debug.subgroup('{ Toggle Data State }');

    const newState = toggle.getAttribute('data-state') === 'on' ? 'off' : 'on';
    toggle.setAttribute('data-state', newState);

    if (type === 'swap') {
        const baseName = toCapitalCase(
            toggle.id.replace('ui-toggle-', '')
        );
        const C = DOM.overlay?.toggles ?? DOM.motherboard?.toggles;
        const nowEl  = C[`swap${baseName}Now`];
        const nextEl = C[`swap${baseName}Next`];
        const delay = fast ? 10 : 50;

        // VALIDATE NEW DOM ELEMENTS
        if (!nowEl || !nextEl) {
            Debug.open('« ERROR: TOGGLE SWAP »');
            Debug.error(`Missing swap elements for ${baseName}`);
            Debug.end();
            return;
        }

        // DATA STATE TOGGLE
        if (newState === 'on') {
            hideContent(nowEl, `${caller} -h ${nowEl.id}`, undefined, undefined, fast);
            showContent(nextEl, `${caller} -s ${nextEl.id}`, undefined, delay, fast);
        } else {
            hideContent(nextEl, `${caller} -h ${nextEl.id}`, undefined, undefined, fast);
            showContent(nowEl, `${caller} -s ${nowEl.id}`, undefined, delay, fast);
        }

        Debug.log(` \nSwapped ${baseName}.\n `);
    } else {
        Debug.log(' \nRotated inner icon.\n ');
    }

    Debug.end();
    Debug.log('...toggled data state.\n ');
}
// ASYNC: TOGGLE TIMEZONE
async function toggleTimezone(caller = 'user', fast = false) {
    Debug.group(`[ TOGGLE TIMEZONE ] → ${caller}`);
    Debug.log(' \nToggling timezone...');
    const timezone = DOM.overlay.toggles.toggleTimezone;
    toggleDataState(timezone, caller, 'swap', fast);
    await updateTimezone(caller, fast);
    Debug.log('...toggled timezone.\n ');
    Debug.end();
}
// ASYNC: UPDATE TIMEZONE
async function updateTimezone(caller, fast = false) {
    Debug.log(' \nUpdating timezone...');
    Debug.subgroup('{ Update Timezones }');
    Debug.log(' \n');

    // VARIABLES
    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.CONSTANTS.THRESHOLDS;
    const _C = UI_STATE.OVERLAY.MODULES.CALENDAR;

    // GET VISIBLE RATIO
    const ratio = getVisibleRatio(el);

    const wasPH = _C.TOGGLE.timezone === 'PH';
    _C.TOGGLE.timezone = wasPH ? 'ET' : 'PH';

    const fromR1 = wasPH ? C.contentRowOnePH : C.contentRowOneET;
    const fromR2 = wasPH ? C.contentRowTwoPH : C.contentRowTwoET;
    const toR1   = wasPH ? C.contentRowOneET : C.contentRowOnePH;
    const toR2   = wasPH ? C.contentRowTwoET : C.contentRowTwoPH;

    await hideContent(fromR1, caller, undefined, undefined, undefined, fast);
    showContent(toR1, caller, undefined, undefined, undefined, fast);
    await hideContent(fromR2, caller, undefined, undefined, undefined, fast);
    showContent(toR2, caller, undefined, undefined, undefined, fast);

    Debug.log('\n');
    Debug.end();
    Debug.log(fast ? '...updated timezones [»].\n ' : '...updated timezones [›].\n ');
}
// ASYNC: TOGGLE HOLIDAYS
async function toggleHolidays(caller = 'user', fast = false) {
    Debug.group(`[ TOGGLE HOLIDAYS ] → ${caller}`);
    Debug.log(' \nToggling holidays...');
    const holidays = DOM.overlay.toggles.toggleHolidays;
    await toggleDataState(holidays, caller, fast);
    await updateHolidays(caller, fast);
    Debug.log('...toggled holidays.\n ');
    Debug.end();
}
// ASYNC: UPDATE HOLIDAYS
async function updateHolidays(caller, fast = false) {
    Debug.log(' \nUpdating holidays...');
    Debug.subgroup('{ Update Holidays }');
    Debug.log(' \n');

    const el = DOM.overlay.root.calendar;
    const C = DOM.overlay.content;
    const _S = UI_STATE.OVERLAY.STATE;
    const _T = UI_STATE.OVERLAY.MODULES.CALENDAR.TOGGLE;
    const r5 = C.contentRowFive;
    const r6 = C.contentRowSix;
    const r7 = C.contentRowSeven;

    const ratio = getVisibleRatio(el);
    const delay = fast === true ? 100 : 500;

    _T.holidays = !_T.holidays;

    if (_T.holidays) {
        morphSection('sectionHoliday', caller, 'vm', undefined, fast);
        openSection('sectionHoliday', caller, undefined, undefined, fast);
        await showContent(r5, caller, undefined, undefined, fast);
        await showContent(r6, caller, undefined, undefined, fast);
        await showContent(r7, caller, undefined, undefined, fast);
    } else {
        await hideContent(r7, caller, undefined, undefined, fast);
        unmorphSection('sectionHoliday', caller, 'vm', delay, fast);
        closeSection('sectionHoliday', caller, undefined, undefined, fast);
        await hideContent(r6, caller, undefined, undefined, fast);
        await hideContent(r5, caller, undefined, undefined, fast);
    }

    Debug.log('\n');
    Debug.end();
    Debug.log(fast ? '...updated holidays [»]\n ' : '...updated holidays [›]\n ');
}
///////////////////////////////// F U N C T I O N S |||||||||||||
///// S Y S T E M |||||||||||||||||||||||||||||||||||||||||||||||
// GLOBALS
const DOM = {
    overlay: {
        root: {},
        section: {},
        content: {},
        toggles: {},
        data: {},
        office: {
            section: {},
            content: {},
            toggles: {},
            data: {},
            documentation: {
                pitches: {
                    credibility: {},
                    institutional: {},
                    bonds: {},
                    kol: {}
                },
                scripts: {
                    ipo: {},
                    secondary: {}
                },
                scrolls: {
                    closes: {},
                    minimum: {},
                    trial: {}
                },
                strokes: {
                    phrases: {},
                    rebuttals: {}
                },
                technicals: {},
                structure: {
                    agent: {
                        profile: {},
                        biography: {}
                    },
                    company: {
                        profile: {},
                        location: {}
                    },
                    process: {
                        banking: {},
                        regulation: {},
                        transfer: {}
                    }
                }
            },
            information: {},
            tools: {},
            options: {}
        }
    },
    motherboard: {
        root: {},
        section: {},
        content: {},
        toggles: {},
        data: {}
    }
};
// CACHE DOM
function cacheDOM() {
    DOM.overlay = {
        root: {
            calendar: document.getElementById('overlayCalendar')
        },
        section: {
            sectionToday: document.getElementById('sectionToday'),
            sectionHoliday: document.getElementById('sectionHoliday'),
            sectionControl: document.getElementById('sectionControl')
        },
        content: {
            // CONTAINERS
            contentToday: document.getElementById('contentToday'),
            contentHoliday: document.getElementById('contentHoliday'),
            contentControl: document.getElementById('contentControl'),
            // ROWS
            contentRowZero: document.getElementById('contentRowZero'),
            contentRowOnePH: document.getElementById('contentRowOnePH'),
            contentRowOneET: document.getElementById('contentRowOneET'),
            contentRowTwoPH: document.getElementById('contentRowTwoPH'),
            contentRowTwoET: document.getElementById('contentRowTwoET'),
            contentRowThree: document.getElementById('contentRowThree'),
            contentRowFour: document.getElementById('contentRowFour'),
            contentRowFive: document.getElementById('contentRowFive'),
            contentRowSix: document.getElementById('contentRowSix'),
            contentRowSeven: document.getElementById('contentRowSeven')
        },
        toggles: {
            toggleHolidays: document.getElementById('ui-toggle-holidays'),
            rotateHolidays: document.getElementById('ui-toggle-rotate-holidays'),
            toggleTimezone: document.getElementById('ui-toggle-timezone'),
            swapTimezoneNow: document.getElementById('ui-swap-timezone-now'),
            swapTimezoneNext: document.getElementById('ui-swap-timezone-next')
        },
        data: {
            // TODAY
            timeDockedL: document.getElementById('cal-time-docked-l'),
            timeDockedR: document.getElementById('cal-time-docked-r'),
            timePH: document.getElementById('cal-time-ph'),
            timeET: document.getElementById('cal-time-et'),
            datePH: document.getElementById('cal-date-ph'),
            dateET: document.getElementById('cal-date-et'),
            marketState: document.getElementById('cal-market-state'),
            marketCount: document.getElementById('cal-market-count'),
            // HOLIDAY
            holidayName: document.getElementById('cal-holiday-name'),
            holidayDate: document.getElementById('cal-holiday-date'),
            holidayCount: document.getElementById('cal-holiday-count')
        },
    };
    DOM.motherboard = {
        root: {
            main: document.getElementById('sectionMain'),
            dashboard: document.getElementById('sectionDashboard'),
            overview: document.getElementById('sectionOverview'),
            news: document.getElementById('sectionNews')
        },
        section: {
            // MAIN
            sectionMain: document.getElementById('sectionMain'),
            sectionInfo: document.getElementById('sectionInfo'),
            sectionMessage: document.getElementById('sectionMessage'),
            // DASHBORD
            sectionDashboard: document.getElementById('sectionDashboard'),
            sectionSettings: document.getElementById('sectionSettings'),
            // OVERVIEW
            sectionOverview: document.getElementById('sectionOverview'),
            sectionDescription: document.getElementById('sectionDescription'),
            sectionRatings: document.getElementById('sectionRatings'),
            // NEWS
            sectionNews: document.getElementById('sectionNews')
        },
        content: {
            // HEAD
            headDashboard: document.getElementById('headDashboard'),
            headSettings: document.getElementById('headSettings'),
            headOverview: document.getElementById('headOverview'),
            headDescription: document.getElementById('headDescription'),
            headRatings: document.getElementById('headRatings'),
            headNews: document.getElementById('headNews'),
            // TITLE
            titleDashboard: document.getElementById('titleDashboard'),
            titleSettings: document.getElementById('titleSettings'),
            titleOverview: document.getElementById('titleOverview'),
            titleDescription: document.getElementById('titleDescription'),
            titleRatings: document.getElementById('titleRatings'),
            titleNews: document.getElementById('titleNews'),
            // CONTENT
            contentMain: document.getElementById('contentMain'),
            contentInfo: document.getElementById('contentInfo'),
            contentMessage: document.getElementById('contentMessage'),
            contentDashboard: document.getElementById('contentDashboard'),
            contentSettings: document.getElementById('contentSettings'),
            contentOverview: document.getElementById('contentOverview'),
            contentDescription: document.getElementById('contentDescription'),
            contentRatings: document.getElementById('contentRatings'),
            contentNews: document.getElementById('contentNews')
        },
        toggles: {
            // MAIN
            inputTicker: document.getElementById('ui-input-ticker'),
            buttonSearch: document.getElementById('ui-button-search'),
            // DASHBOARD
            toggleDashboard: document.getElementById('ui-toggle-dashboard'),
            toggleSettings: document.getElementById('ui-toggle-settings'),
            toggleContainer: document.getElementById('containerDashboard'),
            rotateDashboard: document.getElementById('ui-toggle-rotate-dashboard'),
            rotateSettings: document.getElementById('ui-toggle-rotate-settings'),
            buttonReset: document.getElementById('ui-button-reset'),
            buttonSave: document.getElementById('ui-button-save'),
            inputDiscount: document.getElementById('ui-input-discount'),
            inputFee: document.getElementById('ui-input-fee'),
            inputMinPercent: document.getElementById('ui-input-min-percent'),
            inputMaxPercent: document.getElementById('ui-input-max-percent'),
            // OVERVIEW
            toggleOverview: document.getElementById('ui-toggle-overview'),
            toggleDescription: document.getElementById('ui-toggle-description'),
            toggleRatings: document.getElementById('ui-toggle-ratings'),
            rotateOverview: document.getElementById('ui-toggle-rotate-overview'),
            rotateDescription: document.getElementById('ui-toggle-rotate-description'),
            rotateRatings: document.getElementById('ui-toggle-rotate-ratings'),
            // NEWS
            toggleNews: document.getElementById('ui-toggle-news'),
            rotateNews: document.getElementById('ui-toggle-rotate-news'),
            toggleType: document.getElementById('ui-toggle-type'),
            swapTypeNow: document.getElementById('ui-swap-type-now'),
            swapTypeNext: document.getElementById('ui-swap-type-next'),
            toggleDirection: document.getElementById('ui-toggle-direction'),
            swapDirectionNow: document.getElementById('ui-swap-direction-now'),
            swapDirectionNext: document.getElementById('ui-swap-direction-next'),
            dropdownUnit: document.getElementById('ui-dropdown-range-unit'),
            dropdownValue: document.getElementById('ui-dropdown-range-value'),
            buttonFetch: document.getElementById('ui-button-fetch')
        },
        data: {
            // MAIN: INFORMATION
            displayCompany: document.getElementById('displayCompany'),
            displayPrice: document.getElementById('displayPrice'),
            displayChange: document.getElementById('displayChange'),
            // MAIN: MESSAGE
            messageIndicator: document.getElementById('messageIndicator'),
            messageText: document.getElementById('messageText'),
            // DASHBOARD
            dispName: document.getElementById('dispName'),
            dispTickerExchange: document.getElementById('dispTickerExchange'),
            dispPrice: document.getElementById('dispPrice'),
            dispChange: document.getElementById('dispChange'),
            dispBid: document.getElementById('dispBid'),
            dispDiscount: document.getElementById('dispDiscount'),
            dispMinPrice: document.getElementById('dispMinPrice'),
            dispMinProfit: document.getElementById('dispMinProfit'),
            dispMaxPrice: document.getElementById('dispMaxPrice'),
            dispMaxProfit: document.getElementById('dispMaxProfit'),
            // DASHBOARD: PRICE TABLE
            tableBody: document.getElementById('tableBody'),
            // DASHBOARD PRICE TABLE: BLOCK
            dispBlockMin: document.getElementById('dispBlockMin'),
            dispBlockMinDouble: document.getElementById('dispBlockMinDouble'),
            dispBlockMaxHalf: document.getElementById('dispBlockMaxHalf'),
            dispBlockMax: document.getElementById('dispBlockMax'),
            // DASHBOARD PRICE TABLE: COMMS
            dispCommsMin: document.getElementById('dispCommsMin'),
            dispCommsMinDouble: document.getElementById('dispCommsMinDouble'),
            dispCommsMaxHalf: document.getElementById('dispCommsMaxHalf'),
            dispCommsMax: document.getElementById('dispCommsMax'),
            // DASHBOARD PRICE TABLE: COST
            dispCostMin: document.getElementById('dispCostMin'),
            dispCostMinDouble: document.getElementById('dispCostMinDouble'),
            dispCostMaxHalf: document.getElementById('dispCostMaxHalf'),
            dispCostMax: document.getElementById('dispCostMax'),
            // DASHBOARD PRICE TABLE: TOTAL
            dispTotalMin: document.getElementById('dispTotalMin'),
            dispTotalMinDouble: document.getElementById('dispTotalMinDouble'),
            dispTotalMaxHalf: document.getElementById('dispTotalMaxHalf'),
            dispTotalMax: document.getElementById('dispTotalMax'),
            // DASHBOARD PRICE TABLE: SELL
            dispSellMin: document.getElementById('dispSellMin'),
            dispSellMinDouble: document.getElementById('dispSellMinDouble'),
            dispSellMaxHalf: document.getElementById('dispSellMaxHalf'),
            dispSellMax: document.getElementById('dispSellMax'),
            // DASHBOARD PRICE TABLE: PROFIT
            dispProfitMin: document.getElementById('dispProfitMin'),
            dispProfitMinDouble: document.getElementById('dispProfitMinDouble'),
            dispProfitMaxHalf: document.getElementById('dispProfitMaxHalf'),
            dispProfitMax: document.getElementById('dispProfitMax'),
            // OVERVIEW: INFORMATION
            displayName: document.getElementById('displayName'),
            displayTicker: document.getElementById('displayTicker'),
            displayExchange: document.getElementById('displayExchange'),
            displaySector: document.getElementById('displaySector'),
            displayIndustry: document.getElementById('displayIndustry'),
            displayCountry: document.getElementById('displayCountry'),
            displayWebsite: document.getElementById('displayWebsite'),
            displayMarketPrice: document.getElementById('displayMarketPrice'),
            displayMarketCap: document.getElementById('displayMarketCap'),
            displayWeekLow: document.getElementById('displayWeekLow'),
            displayWeekHigh: document.getElementById('displayWeekHigh'),
            displayTargetPrice: document.getElementById('displayTargetPrice'),
            // OVERVIEW: DESCRIPTION
            dispDescription: document.getElementById('dispDescription'),
            // OVERVIEW: RATINGS
            containerIndicator: document.getElementById('containerIndicator'),
            shapeTriangle: document.getElementById('shapeTriangle'),
            dispPercentage: document.getElementById('dispPercentage'),
            dispStrongSell: document.getElementById('dispStrongSell'),
            dispSell: document.getElementById('dispSell'),
            dispHold: document.getElementById('dispHold'),
            dispBuy: document.getElementById('dispBuy'),
            dispStrongBuy: document.getElementById('dispStrongBuy')
        }
    }

    const countOver= Object.entries(DOM.overlay).length;
    const countOverRoot = Object.entries(DOM.overlay.root).length;
    const countOverSec = Object.entries(DOM.overlay.section).length;
    const countOverCont = Object.entries(DOM.overlay.content).length;
    const countOverCtrl = Object.entries(DOM.overlay.toggles).length;
    const countOverData = Object.entries(DOM.overlay.data).length;
    const countMotherRoot = Object.entries(DOM.motherboard.root).length;
    const countMotherSec = Object.entries(DOM.motherboard.section).length;
    const countMotherCont = Object.entries(DOM.motherboard.content).length;
    const countMotherCtrl = Object.entries(DOM.motherboard.toggles).length;
    const countMotherData = Object.entries(DOM.motherboard.data).length;

    const totalOver = countOverSec + countOverCont + countOverCtrl + countOverData;
    const totalMother = countMotherSec + countMotherCont + countMotherCtrl + countMotherData;

    const total = totalOver + totalMother; 

    Debug.group('[ CACHE DOM ]');

    Debug.subgroup('< Cache DOM Details >');

    Debug.subgroup('-----------------------:: ROOT');
    Debug.log('- Overlay root:', countOverRoot);
    Debug.log('- Motherboard root:', countMotherRoot);
    Debug.log(' \n= SUBTOTAL:', countOverRoot + countMotherRoot);
    Debug.end();

    Debug.subgroup('--------------------|| OVERLAY');
    Debug.log('- Section entries:', countOverSec);
    Debug.log('- Content entries:', countOverCont);
    Debug.log('- Control entries:', countOverCtrl);
    Debug.log('- Data entries:', countOverData);
    Debug.log(' \n= SUBTOTAL:', countOverSec + countOverCont + countOverCtrl + countOverData);
    Debug.end();

    Debug.subgroup('----------------|| MOTHERBOARD');
    Debug.log('- Section entries:', countMotherSec);
    Debug.log('- Content entries:', countMotherCont);
    Debug.log('- Control entries:', countMotherCtrl);
    Debug.log('- Data entrie:', countMotherData);
    Debug.log(' \n= SUBTOTAL:', countMotherSec + countMotherCont + countMotherCtrl + countMotherData);
    Debug.log('------------------------------');
    Debug.end();

    Debug.log('  = TOTAL ENTRIES:', totalOver + totalMother + countOverRoot + countMotherRoot);
    Debug.end();
    Debug.end();
}
// VALIDATE DOM
function validateDOM(group, path = '') {
    Object.entries(group).forEach(([key, value]) => {
        const fullPath = path ? `${path}.${key}` : key;
        if (value && typeof value === 'object' && !(value instanceof HTMLElement)) {
            validateDOM(value, fullPath);
        } else if (!value) {
            Debug.open('« ERROR: VALIDATE DOM »');
            Debug.error(`Missing DOM node: ${fullPath}`);
        }
    });
}
// INIT UI BINDINGS
function initUIBindings() {
    Debug.group('[ INIT UI BINDINGS ]');

    const holidays = DOM.overlay.toggles.toggleHolidays;
    const timezone = DOM.overlay.toggles.toggleTimezone;
    const T = DOM.motherboard.toggles;
    const input = T.inputTicker;
    const search = T.buttonSearch;
    const dashboard = T.toggleDashboard;
    const settings = T.toggleSettings;
    const reset = T.buttonReset;
    const save = T.buttonSave;
    const discout = T.inputDiscount;
    const fee = T.inputFee;
    const minpercent = T.inputMinPercent;
    const maxpercent = T.inputMaxPercent;
    const overview = T.toggleOverview;
    const description = T.toggleDescription;
    const ratings = T.toggleRatings;
    const news = T.toggleNews;
    const type = T.toggleType;
    const direction = T.toggleDirection;
    const unit = T.dropdownUnit;
    const value = T.dropdownValue;
    const fetch = T.buttonFetch;

    holidays.addEventListener('click', () => toggleHolidays('user'));
    timezone.addEventListener('click', () => toggleTimezone('user'));

    Debug.log(' \nUI element:', holidays.id);
    Debug.log('UI element:', timezone.id, '\n ');
    /*
    Debug.log('UI element:', input.id);
    Debug.log('UI element:', search.id);
    Debug.log('UI element:', dashboard.id);
    Debug.log('UI element:', settings.id);
    Debug.log('UI element:', reset.id);
    Debug.log('UI element:', save.id);
    Debug.log('UI element:', discount.id);
    Debug.log('UI element:', fee.id);
    Debug.log('UI element:', minpercent.id);
    Debug.log('UI element:', maxpercent.id);
    Debug.log('UI element:', overview.id);
    Debug.log('UI element:', description.id);
    Debug.log('UI element:', ratings.id);
    Debug.log('UI element:', news.id);
    Debug.log('UI element:', type.id);
    Debug.log('UI element:', direction.id);
    Debug.log('UI element:', unit.id);
    Debug.log('UI element:', value.id);
    Debug.log('UI element:', fetch.id);
    */
    Debug.end();
}
// ROUTER
function router() {
    Debug.group('[ ROUTER: RUN-TIME SPLIT ]');

    const isFirstRun = !localStorage.getItem(STORAGE_KEYS.SESSION);
    DateCache.save(STORAGE_KEYS.SESSION, true, 'static');
    let type = '';
    if (isFirstRun) {
        type = 'First run'
        DateCache.save(STORAGE_KEYS.ACTIVE_SETTINGS, DEFAULT_SETTINGS, 'static');
        DateCache.save(STORAGE_KEYS.ACTIVE_FEED, DEFAULT_FEED, 'static');
        Debug.log(' \nDefault values saved for settings and active news feed. \nFirst run session flag planted.\n ');
    } else {
        type = 'Continuation'
        Debug.log(' \nDiscovered previous session flag. \nChecking validity of previous sessions data.\n ');
    }
    Debug.log('Session type:', type);
    Debug.end();
}
// ASYNC: RUN METRICS PIPELINE
async function runMetricsPipeline() {
    Debug.group('[ METRICS PIPELINE ]');

    if (!activeTicker) {
        Debug.open('« ERROR »');
        Debug.error(`Invalid active ticker symbol: ${activeTicker}`);
        Debug.end();
        return;
    }

    let status = '';
    const {
        isMarketOpen
    } = MarketGate.getState();
    if (isMarketOpen) {
        status = 'Open';
        const quoteData = await fetchAlphaVantageQuote(activeTicker);
        const {
            metricsRaw
        } = calculateFMS(quoteData, settings);
        const formatted = DateCache.format.metrics(metricsRaw);
        renderMetrics(formatted);
    } else {
        status = 'Closed';
        runNormalMetricsFlow(activeTicker);
    }

    Debug.log(' \nMarket is open:', isMarketOpen, '\n ');
    Debug.end();
}
// ASYNC: INITIALIZE
async function init() {
    Debug.group('[ DATE CACHE ]');
    await DateCache.holidays.getHolidayCalendar();
    Debug.end();
}
// DOM: APP ENTRY POINT
document.addEventListener('DOMContentLoaded', async () => {
    Debug.group('-------------|| DOM: BIOS BOOT SEQUENCE');

    // DEV ONLY
    localStorage.clear();

    // DOM SETUP
    cacheDOM();
    validateDOM(DOM);

    // DATA INIT
    await init();

    // INITIAL RENDER (ONCE)
    const nowEpoch = Math.floor(Date.now() / 1000);
    const market = DateCache.market.getState(nowEpoch);

    // SYSTEM SELF VALIDATION
    const next = market.holidays.next;
    Debug.log('Post close:', next.postClose); // ← BUG: POST CLOSE IS 'UNDEFINED'
    // Debug.log(formatDateTime(next.postClose, 'MNL'));

    // RENDER OVERLAY: CALENDAR
    renderCalendar(market);

    // BASE LAYOUT (NO ANIMATION)
    applyInitialState();

    // MEASURE AFTER DOM IS STABLE
    measureAnimations();

    // START CLOCK ENGINE
    ClockUpdater.start();
    const timestamp = Date.now();
    renderTimezones(calculateTimezones(timestamp));

    // ROUTING
    router();

    // UI BINDINGS
    initUIBindings();
    const dragZones = [
        DOM.overlay.section.sectionToday,
        DOM.overlay.section.sectionHoliday,
        DOM.overlay.section.sectionControl
    ];
    dragZones.forEach(zone => {
        zone.addEventListener('pointerdown', onPointerDown);
        zone.addEventListener('dblclick', onDoubleClick);
    });

    Debug.end();
    ClockUpdater.stop();
    /*console.clear();*/
});
///////////////////////////// E N D - O F - L I N E |||||||||||||
///////////////////////////////////////////////////////( m//||||||||



// 1. ASK ME CLARIFYING QUESTIONS UNTIL YOU ARE AT 95% CONFIDENT THAT YOU CAN COMPLETE THIS TASK SUCCESFULLY.
// 2. WHAT WOULD A 0.1% PERSON IN THIS FIELD THINK?
// 3. REFRAME THIS IN A WAY THAT CHANGES THE WAY I SEE THE PROBLEM.


