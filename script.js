// ── GLOBAL VARIABLES ─────────────────────────────────────
const PASSWORD = "";
const ALPHA_VANTAGE_KEY = 'ONWS7QAI76ZRNLON';
const ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query?';

let currentStock = null;
let currentSettings = null;
let currentTicker = null;
let isDefault = null;
let fee = "buy";
let mode = "high";
let frozenL = "";
let frozenR = "";
let fullDesc = "hide";
let newsFilter = 'all';
let devModeUnlocked = false;
let devModeInitialized = false;
let lastApiCallTime = 0;

// Secondary dev mode states
let secondaryDevActive = null; // 'company' or 'price' or null
let companyInputActive = false;
let priceInputActive = false;
let companyTaps = 0;
let priceTaps = 0;
let companyTapTimeout = null;
let priceTapTimeout = null;

// Track which was last updated by dev mode
let lastDevUpdate = null; // 'company' or 'price' or null

const DEFAULT_MINIMUM_THRESHOLD = 5000;
const PRICE_ROUNDING_INTERVALS = [
    { limit: 5, interval: 0.01 },
    { limit: 10, interval: 0.05 },
    { limit: 25, interval: 0.1 },
    { limit: 50, interval: 0.25 },
    { limit: 100, interval: 0.5 },
    { limit: 250, interval: 1 },
    { limit: 500, interval: 2.5 },
    { limit: 750, interval: 5 },
    { limit: 1000, interval: 10 },
    { limit: 2500, interval: 25 },
    { limit: 5000, interval: 50 },
    { limit: Infinity, interval: 100 }
];
const SHARE_ROUNDING_INTERVALS = [
    { limit: 10, interval: 1 },
    { limit: 100, interval: 5 },
    { limit: 1000, interval: 10 },
    { limit: 5000, interval: 25 },
    { limit: 10000, interval: 50 },
    { limit: Infinity, interval: 100 }
];

// ── HELPERS ──────────────────────────────────────────────
function getConfig() {
    const type = currentStock[currentTicker].stockType;
    const defaults = currentSettings[type].DEFAULT;
    const modified = currentSettings[type].MODIFIED;

    const keys = [
        "BLOCKAGE_DISCOUNT",
        "BROKERAGE_FEE",
        "BROKERAGE_FEE_SELL",
        "SELL_MIN",
        "SELL_MAX"
    ];

    // determine which keys are effective
    const effectiveKeys = keys.filter(k => modified[k] !== null && modified[k] !== defaults[k]);

    // determine modifiedState
    let modifiedState;
    if (effectiveKeys.length === 0) modifiedState = "null";
    else if (effectiveKeys.length === keys.length) modifiedState = "full";
    else modifiedState = "mix";

    // build merged config — effective modified values, fallback to default
    const merged = {};
    keys.forEach(k => {
        merged[k] = effectiveKeys.includes(k) ? modified[k] : defaults[k];
    });

    // active config for calculations
    const active = isDefault ? defaults : merged;

    // alternative — raw modified for display when modifiedState === 'null'
    const alternative = isDefault ? modified : defaults;

    return {
        active,
        alternative,
        defaults,
        modified,
        modifiedState,
        effectiveKeys
    };
}

function getPriceInterval(val) {
    return (
        PRICE_ROUNDING_INTERVALS.find(r => val < r.limit) || { interval: 100 }
    ).interval;
}

function getShareInterval(val) {
    return (
        SHARE_ROUNDING_INTERVALS.find(r => val < r.limit) || { interval: 100 }
    ).interval;
}

// ── ALPHA VANTAGE API ────────────────────────────────────
async function throttledApiCall() {
    const now = Date.now();
    const timeSinceLastCall = now - lastApiCallTime;
    if (timeSinceLastCall < 1000) {
        await new Promise(resolve => setTimeout(resolve, 1000 - timeSinceLastCall));
    }
    lastApiCallTime = Date.now();
}

async function fetchAlphaVantageQuote(ticker) {
    if (!ticker) throw new Error('Ticker symbol required.');
    
    const symbol = String(ticker).trim().toUpperCase();
    await throttledApiCall();
    
    const url = `${ALPHA_VANTAGE_BASE_URL}function=GLOBAL_QUOTE&symbol=${encodeURIComponent(symbol)}&apikey=${ALPHA_VANTAGE_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    
    if (data?.Note || data?.['Error Message']) {
        throw new Error(data?.Note || data?.['Error Message']);
    }
    
    const raw = data?.['Global Quote'];
    if (!raw || !raw['05. price']) {
        throw new Error('Invalid response or ticker not found.');
    }
    
    const rawSymbol = raw['01. symbol'];
    if (!rawSymbol || rawSymbol.toUpperCase() !== symbol) {
        throw new Error(`Ticker mismatch: ${rawSymbol} != ${symbol}`);
    }
    
    const price = Number(raw['05. price']) || 0;
    const change = Number(String(raw['10. change percent'] || '').replace('%', '')) || 0;
    
    return { price, change };
}

async function fetchAlphaVantageOverview(ticker) {
    if (!ticker) throw new Error('Ticker symbol required.');
    
    const symbol = String(ticker).trim().toUpperCase();
    await throttledApiCall();
    
    const url = `${ALPHA_VANTAGE_BASE_URL}function=OVERVIEW&symbol=${encodeURIComponent(symbol)}&apikey=${ALPHA_VANTAGE_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    
    if (data?.Note || data?.['Error Message']) {
        throw new Error(data?.Note || data?.['Error Message']);
    }
    
    if (!data || typeof data !== 'object' || !data.Name) {
        throw new Error('Malformed response or ticker not found.');
    }
    
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
}

// ── SERIAL GENERATION ────────────────────────────────────
function generateSerial(ticker, stockType, settings) {
    // Determine prefix
    const prefix = stockType === 'PUBLIC' ? 'plc' : 'pvt';
    
    // Clean ticker (remove .PVT suffix if exists)
    const tickerClean = ticker.replace(/\.PVT$/i, '');
    
    // Get next market open epoch from DateCache
    const marketState = DateCache.market.getState(Math.floor(Date.now() / 1000));
    const nextOpenEpoch = marketState.nextEvent.epoch;
    
    // Build settings key
    const blockage = settings.BLOCKAGE_DISCOUNT.toFixed(2);
    const feeBuy = settings.BROKERAGE_FEE.toFixed(2);
    const feeSell = settings.BROKERAGE_FEE_SELL.toFixed(2);
    const sellMin = settings.SELL_MIN.toFixed(1);
    const sellMax = settings.SELL_MAX.toFixed(1);
    
    // Include sell fee only if different from buy fee
    const sellFeeStr = feeBuy !== feeSell ? `_${feeSell}` : '';
    
    const serial = `${prefix}.${tickerClean}_v${blockage}.${feeBuy}${sellFeeStr}_${sellMin}${sellMax}.${nextOpenEpoch}`;
    return serial;
}

// ── LOCALSTORAGE MANAGEMENT ──────────────────────────────
function initDevModeStorage() {
    if (devModeInitialized) return;
    
    // Copy portfolio and settings from JSON to localStorage
    localStorage.setItem('fms-portfolio', JSON.stringify(currentStock));
    localStorage.setItem('fms-settings', JSON.stringify(currentSettings));
    localStorage.setItem('fms-dev-mode', 'true');
    
    devModeInitialized = true;
}

function getDevModeData(ticker, key) {
    // If dev mode initialized, read from localStorage
    if (devModeInitialized) {
        const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
        return portfolio[ticker]?.[key] || null;
    }
    return null;
}

function saveDevModeData(ticker, data) {
    const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
    
    if (!portfolio[ticker]) {
        portfolio[ticker] = currentStock[ticker] || {};
    }
    
    portfolio[ticker] = { ...portfolio[ticker], ...data };
    localStorage.setItem('fms-portfolio', JSON.stringify(portfolio));
}

function isDataExpired(serial) {
    if (!serial) return true;
    
    // Extract epoch from serial (last segment after final dot)
    const parts = serial.split('.');
    const serialEpoch = parseInt(parts[parts.length - 1]);
    
    // Check if currently in market hours
    const now = Math.floor(Date.now() / 1000);
    const marketState = DateCache.market.getState(now);
    
    // If market is open, data is expired
    if (marketState.isOpen) return true;
    
    // If not in market hours, check if serial expiration > now
    return serialEpoch <= now;
}



// ── DEV MODE TAP COUNTER ─────────────────────────────────
let devModeTaps = 0;
let devModeTapTimeout = null;
let devModeCountdownActive = false;

function showDevModeCountdown(remaining) {
    // Create or update countdown toast
    let toast = document.getElementById('dev-mode-toast');
    
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'dev-mode-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 107, 43, 0.9);
            color: #fff;
            padding: 12px 24px;
            border-radius: 4px;
            font-family: 'Rajdhani', sans-serif;
            font-size: 12px;
            letter-spacing: 0.1em;
            z-index: 1000;
            animation: fadeInOut 2s ease-in-out;
            pointer-events: none;
        `;
        document.body.appendChild(toast);
    }
    
    toast.textContent = `DEV MODE: ${remaining} TAP${remaining === 1 ? '' : 'S'} REMAINING`;
    toast.style.opacity = '1';
    
    // Auto-hide after 2 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
    }, 1500);
}

function resetDevModeTaps() {
    devModeTaps = 0;
    if (devModeTapTimeout) clearTimeout(devModeTapTimeout);
}

function handleXerxesFMSTab() {
    if (devModeUnlocked) {
        // Show "already a developer" message
        let toast = document.getElementById('dev-already-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'dev-already-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(255, 107, 43, 0.9);
                color: #fff;
                padding: 12px 24px;
                border-radius: 4px;
                font-family: 'Rajdhani', sans-serif;
                font-size: 12px;
                letter-spacing: 0.1em;
                z-index: 1000;
                animation: fadeInOut 2s ease-in-out;
                pointer-events: none;
            `;
            document.body.appendChild(toast);
        }
        
        toast.textContent = 'You are already a developer';
        toast.style.opacity = '1';
        
        setTimeout(() => {
            toast.style.opacity = '0';
        }, 1500);
        return;
    }
    
    devModeTaps++;
    showDevModeCountdown(7 - devModeTaps);
    
    // Reset counter after 3 seconds of inactivity
    if (devModeTapTimeout) clearTimeout(devModeTapTimeout);
    devModeTapTimeout = setTimeout(resetDevModeTaps, 3000);
    
    if (devModeTaps >= 7) {
        unlockDevMode();
        resetDevModeTaps();
    }
}

function unlockDevMode() {
    devModeUnlocked = true;
    initDevModeStorage();
    
    // Change theme for title, price value, and company name
    const titleEl = document.querySelector('h1 span');
    const priceEl = document.getElementById('price');
    const nameEl = document.getElementById('name');
    
    const fieryGradient = 'linear-gradient(135deg, #ff6b2b 0%, #ff3a00 50%, #ff1a00 100%)';
    
    if (titleEl) {
        titleEl.style.background = fieryGradient;
        titleEl.style.webkitBackgroundClip = 'text';
        titleEl.style.webkitTextFillColor = 'transparent';
        titleEl.style.backgroundClip = 'text';
    }
    
    if (priceEl) {
        priceEl.style.background = fieryGradient;
        priceEl.style.webkitBackgroundClip = 'text';
        priceEl.style.webkitTextFillColor = 'transparent';
        priceEl.style.backgroundClip = 'text';
    }
    
    if (nameEl) {
        nameEl.style.background = fieryGradient;
        nameEl.style.webkitBackgroundClip = 'text';
        nameEl.style.webkitTextFillColor = 'transparent';
        nameEl.style.backgroundClip = 'text';
    }
    
    console.log('✓ Dev Mode Unlocked');
}

// ── SECONDARY DEV MODE: COMPANY NAME INPUT ───────────────
function handleCompanyNameTap() {
    if (!devModeUnlocked) return;
    if (secondaryDevActive && secondaryDevActive !== 'company') return; // Other input active
    
    companyTaps++;
    showDevModeCountdown(7 - companyTaps);
    
    if (companyTapTimeout) clearTimeout(companyTapTimeout);
    companyTapTimeout = setTimeout(() => {
        companyTaps = 0;
    }, 3000);
    
    if (companyTaps >= 7) {
        unlockCompanyInput();
        companyTaps = 0;
    }
}

function unlockCompanyInput() {
    // Close price input if active
    if (priceInputActive) {
        closePriceInput();
    }
    
    companyInputActive = true;
    secondaryDevActive = 'company';
    
    // Hide company name, show input
    const nameEl = document.getElementById('name');
    nameEl.style.display = 'none';
    
    // Create input field
    let input = document.getElementById('dev-company-input');
    if (!input) {
        input = document.createElement('input');
        input.id = 'dev-company-input';
        input.type = 'text';
        input.placeholder = 'Enter ticker symbol or company name';
        input.style.cssText = `
            flex: 1;
            background: rgba(19, 19, 33, 0.8);
            border: 1px solid #2e2134;
            color: #cdd6f8;
            font-family: 'Inconsolata', monospace;
            font-size: 1.5rem;
            letter-spacing: 0.5rem;
            padding: 8px 12px;
            border-radius: 4px;
            outline: none;
            transition: border-color 0.2s;
        `;
        
        input.addEventListener('focus', (e) => {
            e.target.style.borderColor = '#69e5ff';
        });
        
        input.addEventListener('blur', (e) => {
            e.target.style.borderColor = '#2e2134';
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                submitCompanySearch();
            }
        });
        
        nameEl.parentNode.insertBefore(input, nameEl);
    }
    
    input.style.display = 'block';
    input.focus();
    
    // Show search button
    showSearchButton();
}

function closeCompanyInput() {
    companyInputActive = false;
    
    const nameEl = document.getElementById('name');
    const input = document.getElementById('dev-company-input');
    
    if (input) input.style.display = 'none';
    if (nameEl) nameEl.style.display = 'inline';
    
    if (secondaryDevActive === 'company') {
        secondaryDevActive = null;
    }
}

async function submitCompanySearch() {
    const input = document.getElementById('dev-company-input');
    if (!input || !input.value.trim()) {
        console.warn('Empty ticker input');
        return;
    }
    
    const ticker = input.value.trim().toUpperCase();
    
    try {
        // Fetch quote first
        console.log(`Fetching data for ${ticker}...`);
        const quote = await fetchAlphaVantageQuote(ticker);
        
        // Wait 1+ second, then fetch overview
        await new Promise(r => setTimeout(r, 1100));
        const overview = await fetchAlphaVantageOverview(ticker);
        
        // Store in localStorage
        const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
        portfolio[ticker] = {
            stockType: 'PUBLIC', // Default to PUBLIC for new searches
            default: true,
            price: quote.price,
            COMPANY: overview,
            FINANCIALS: {
                change: quote.change,
                marketCap: overview.marketCap,
                weekLow: overview.weekLow,
                weekHigh: overview.weekHigh,
                yearTarget: overview.target
            },
            FUNDING: {
                fundingToDate: null,
                latestAmountRaised: null,
                latestFundingDate: null,
                latestShareClass: '',
                leadInvestor: '',
                totalFundingRounds: null
            },
            NEWS: [],
            RATINGS: {
                analystCount: null,
                recommendationKey: '',
                recommendationMean: null,
                strongBuy: overview.ratings?.strongBuy || 0,
                buy: overview.ratings?.buy || 0,
                hold: overview.ratings?.hold || 0,
                sell: overview.ratings?.sell || 0,
                strongSell: overview.ratings?.strongSell || 0
            }
        };
        
        localStorage.setItem('fms-portfolio', JSON.stringify(portfolio));
        
        // Update dropdown and switch to new ticker
        updateDropdownFromStorage();
        renderTicker(ticker);
        
        // Lock dev mode but keep company name themed
        lastDevUpdate = 'company';
        lockSecondaryDevMode();
        applyDevThemeToLastUpdate();
        
        console.log(`✓ ${ticker} fetched and stored`);
    } catch (error) {
        console.error('Search failed:', error.message);
        alert(`❌ Search failed: ${error.message}`);
    }
}

// ── SECONDARY DEV MODE: PRICE INPUT ──────────────────────
function handlePriceTap() {
    if (!devModeUnlocked) return;
    if (secondaryDevActive && secondaryDevActive !== 'price') return; // Other input active
    
    priceTaps++;
    showDevModeCountdown(7 - priceTaps);
    
    if (priceTapTimeout) clearTimeout(priceTapTimeout);
    priceTapTimeout = setTimeout(() => {
        priceTaps = 0;
    }, 3000);
    
    if (priceTaps >= 7) {
        unlockPriceInput();
        priceTaps = 0;
    }
}

function unlockPriceInput() {
    // Close company input if active
    if (companyInputActive) {
        closeCompanyInput();
    }
    
    priceInputActive = true;
    secondaryDevActive = 'price';
    
    // Hide price value, show input
    const priceEl = document.getElementById('price');
    const currentPrice = priceEl.textContent;
    priceEl.style.display = 'none';
    
    // Create input field
    let input = document.getElementById('dev-price-input');
    if (!input) {
        input = document.createElement('input');
        input.id = 'dev-price-input';
        input.type = 'text';
        input.placeholder = currentPrice;
        input.style.cssText = `
            background: rgba(19, 19, 33, 0.8);
            border: 1px solid #2e2134;
            color: #cdd6f8;
            font-family: 'Inconsolata', monospace;
            font-size: 1rem;
            padding: 8px 12px;
            border-radius: 4px;
            outline: none;
            width: 120px;
            transition: border-color 0.2s;
        `;
        
        input.addEventListener('focus', (e) => {
            e.target.style.borderColor = '#69e5ff';
        });
        
        input.addEventListener('blur', (e) => {
            e.target.style.borderColor = '#2e2134';
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                submitPriceUpdate();
            }
        });
        
        priceEl.parentNode.insertBefore(input, priceEl);
    }
    
    input.style.display = 'inline-block';
    input.focus();
    
    // Show search button
    showSearchButton();
}

function closePriceInput() {
    priceInputActive = false;
    
    const priceEl = document.getElementById('price');
    const input = document.getElementById('dev-price-input');
    
    if (input) input.style.display = 'none';
    if (priceEl) priceEl.style.display = 'inline';
    
    if (secondaryDevActive === 'price') {
        secondaryDevActive = null;
    }
}

async function submitPriceUpdate() {
    const input = document.getElementById('dev-price-input');
    const placeholder = input.placeholder;
    const inputValue = input.value.trim();
    
    let newPrice = null;
    
    try {
        if (!inputValue || inputValue === placeholder) {
            // Fetch from Alpha Vantage
            console.log(`Fetching latest price for ${currentTicker}...`);
            const quote = await fetchAlphaVantageQuote(currentTicker);
            newPrice = quote.price;
            const newChange = quote.change;
            
            // Update localStorage
            const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
            if (portfolio[currentTicker]) {
                portfolio[currentTicker].price = newPrice;
                portfolio[currentTicker].FINANCIALS.change = newChange;
                localStorage.setItem('fms-portfolio', JSON.stringify(portfolio));
            }
        } else {
            // Use manual input
            newPrice = parseFloat(inputValue);
            if (isNaN(newPrice)) {
                throw new Error('Invalid price');
            }
            
            // Update localStorage
            const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
            if (portfolio[currentTicker]) {
                portfolio[currentTicker].price = newPrice;
                localStorage.setItem('fms-portfolio', JSON.stringify(portfolio));
            }
        }
        
        // Recalculate and re-render
        renderTicker(currentTicker);
        
        // Lock dev mode but keep price themed
        lastDevUpdate = 'price';
        lockSecondaryDevMode();
        applyDevThemeToLastUpdate();
        
        console.log(`✓ Price updated to ${newPrice}`);
    } catch (error) {
        console.error('Price update failed:', error.message);
        alert(`❌ Price update failed: ${error.message}`);
    }
}

// ── SEARCH BUTTON ────────────────────────────────────────
function showSearchButton() {
    let searchBtn = document.getElementById('dev-search-btn');
    
    if (!searchBtn) {
        const tckrSelEl = document.getElementById('ticker-select');
        searchBtn = document.createElement('button');
        searchBtn.id = 'dev-search-btn';
        searchBtn.textContent = 'SEARCH';
        searchBtn.style.cssText = `
            background: linear-gradient(135deg, #ff6b2b 0%, #ff3a00 100%);
            border: none;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 0.5rem;
            transition: opacity 0.2s;
        `;
        
        searchBtn.addEventListener('click', () => {
            if (companyInputActive) submitCompanySearch();
            if (priceInputActive) submitPriceUpdate();
        });
        
        searchBtn.addEventListener('mousedown', () => {
            searchBtn.style.opacity = '0.8';
        });
        
        searchBtn.addEventListener('mouseup', () => {
            searchBtn.style.opacity = '1';
        });
        
        tckrSelEl.parentNode.insertBefore(searchBtn, tckrSelEl.nextSibling);
    }
    
    searchBtn.style.display = 'inline-block';
}

function hideSearchButton() {
    const searchBtn = document.getElementById('dev-search-btn');
    if (searchBtn) searchBtn.style.display = 'none';
}

// ── DEV MODE LOCK/RESET ──────────────────────────────────
function lockSecondaryDevMode() {
    closeCompanyInput();
    closePriceInput();
    hideSearchButton();
    secondaryDevActive = null;
}

function lockAllDevMode() {
    lockSecondaryDevMode();
    devModeUnlocked = false;
    lastDevUpdate = null;
    
    // Revert all themes
    const titleEl = document.querySelector('h1 span');
    const priceEl = document.getElementById('price');
    const nameEl = document.getElementById('name');
    
    if (titleEl) {
        titleEl.style.background = '';
        titleEl.style.webkitBackgroundClip = '';
        titleEl.style.webkitTextFillColor = '';
        titleEl.style.backgroundClip = '';
    }
    
    if (priceEl) {
        priceEl.style.background = '';
        priceEl.style.webkitBackgroundClip = '';
        priceEl.style.webkitTextFillColor = '';
        priceEl.style.backgroundClip = '';
    }
    
    if (nameEl) {
        nameEl.style.background = '';
        nameEl.style.webkitBackgroundClip = '';
        nameEl.style.webkitTextFillColor = '';
        nameEl.style.backgroundClip = '';
    }
    
    resetDevModeTaps();
    console.log('✓ Dev Mode Locked');
}

function applyDevThemeToLastUpdate() {
    const fieryGradient = 'linear-gradient(135deg, #ff6b2b 0%, #ff3a00 50%, #ff1a00 100%)';
    
    if (lastDevUpdate === 'company') {
        const nameEl = document.getElementById('name');
        if (nameEl) {
            nameEl.style.background = fieryGradient;
            nameEl.style.webkitBackgroundClip = 'text';
            nameEl.style.webkitTextFillColor = 'transparent';
            nameEl.style.backgroundClip = 'text';
        }
    } else if (lastDevUpdate === 'price') {
        const priceEl = document.getElementById('price');
        if (priceEl) {
            priceEl.style.background = fieryGradient;
            priceEl.style.webkitBackgroundClip = 'text';
            priceEl.style.webkitTextFillColor = 'transparent';
            priceEl.style.backgroundClip = 'text';
        }
    }
}

// ── UPDATE DROPDOWN FROM LOCALSTORAGE ────────────────────
function updateDropdownFromStorage() {
    const portfolio = JSON.parse(localStorage.getItem('fms-portfolio') || '{}');
    const tickers = Object.keys(portfolio).reverse();
    const tckrSelEl = document.getElementById('ticker-select');
    
    tckrSelEl.innerHTML = '';
    tickers.forEach(ticker => {
        const opt = document.createElement('option');
        opt.value = ticker;
        opt.textContent = ticker;
        tckrSelEl.appendChild(opt);
    });
}

function fmsRoundPrice(val) {
    const step = getPriceInterval(val);
    const factor = 1 / step;
    const lower = Math.floor(val * factor) / factor;
    const upper = Math.ceil(val * factor) / factor;
    if (lower === upper) return lower;
    return val - lower <= upper - val ? lower : upper;
}

function fmsRoundShares(val, bid, feePct) {
    const step = getShareInterval(val);
    const factor = 1 / step;
    const lower = Math.floor(val * factor) / factor;
    const upper = Math.ceil(val * factor) / factor;
    if (lower === upper) return lower;
    const feeMultiplier = 1 + feePct;
    const lowerCost = lower * bid * feeMultiplier;
    if (lowerCost < DEFAULT_MINIMUM_THRESHOLD) return upper;
    return val - lower <= upper - val ? lower : upper;
}

function syncModeUI() {
    document.getElementById('card-min').classList.toggle('active', mode === 'low');
    document.getElementById('card-max').classList.toggle('active', mode === 'high');
    document.querySelectorAll('.tbl-head-row').forEach(row => {
        row.classList.toggle('profit-min', mode === 'low');
        row.classList.toggle('profit-max', mode === 'high');
    });
}

// ── SELECT WIDTH ────────────────────────────────────────────────
function adjustWidth() {
    const tempSpan = document.createElement('span');
    
    const style = window.getComputedStyle(tckrSelEl);
    tempSpan.style.font = style.font;
    tempSpan.style.visibility = 'hidden';
    tempSpan.style.position = 'absolute';
    tempSpan.style.whiteSpace = 'nowrap';
    
    // Set text to current selection
    tempSpan.textContent = tckrSelEl.options[tckrSelEl.selectedIndex].text;
    document.body.appendChild(tempSpan);
    
    // Set select width (add ~30px for the arrow icon)
    const arrowWidth = 30;
    tckrSelEl.style.width = `${tempSpan.offsetWidth + arrowWidth}px`;
    
    document.body.removeChild(tempSpan);
}

//adjustWidth(); 

// ── DATA ────────────────────────────────────────────────
function formatCurrency(v, mc = false) {
    if (!mc) {
        return "$" + v.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
            });
    }

    const absV = Math.abs(v);
    let formatted;

    if (absV >= 1e12) {
        formatted = "$" + (v / 1e12).toFixed(2) + "T";
    } else if (absV >= 1e9) {
        const billion = v / 1e9;
        if (Math.abs(billion) >= 250) {
            formatted = "$" + (billion / 1000).toFixed(2) + "T"; // e.g., 300B → 0.30T
        } else {
            formatted = "$" + billion.toFixed(2) + "B";
        }
    } else if (absV >= 1e6) {
        const million = v / 1e6;
        if (Math.abs(million) >= 250) {
            formatted = "$" + (million / 1000).toFixed(2) + "B"; // e.g., 300M → 0.30B
        } else {
            formatted = "$" + million.toFixed(2) + "M";
        }
    } else if (absV >= 1e3) {
        formatted = "$" + (v / 1e3).toFixed(2) + "K";
    } else {
        formatted = "$" + v.toFixed(2);
    }

    return formatted;
}

function formatDate(d) {
    return d
        .toLocaleDateString("en-US", {
            weekday: "long",
            day: "2-digit",
            month: "short",
            year: "numeric"
        })
        .toUpperCase();
}

function formatDescription() {
    const stock = currentStock[currentTicker];
    if (!stock) throw new Error("ticker not found: " + currentTicker);
    const d = stock.COMPANY.description;
    const p = d.split("\n\n");
    const s = p[0] ? `${p[0]}..` : d;
    return { d, s };
}

function toggleFee() {
    fee = fee === "buy" ? "sell" : "buy";
    const lbl = document.querySelector("#settings-lbl-fee");
    if (lbl) lbl.textContent = fee === "buy" ? "     FEE" : "FEE SELL";
    renderTableSettings();
}

function formatPercent(val, isDecimal = true, interval = 0.5) {
    // Convert decimal to percentage if needed
    const percentage = isDecimal ? val * 100 : val;

    // Round to nearest interval
    const rounded = Math.round(percentage / interval) * interval;

    // Format with minimal decimal places
    return rounded % 1 === 0
        ? `${rounded}%`
        : `${parseFloat(rounded.toFixed(10))}%`;
}

function formatUrl(url) {
    return url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, "").split("/")[0];
}

// ── RENDER ───────────────────────────────────────────────
function renderTablePrice(blocks, bid, feePct, feePctSell, sellMin, sellMax) {
    const tbody = document.getElementById("tbody-price");
    tbody.innerHTML = "";
    
    const feeBuy = 1 + feePct;
    const feeSell = 1 - feePctSell;
    
    blocks.forEach(b => {
        const cost = b * bid * feeBuy;
        const comms = cost - b * bid;
        const total = cost;
        const grossL = b * sellMin;
        const netL = grossL * feeSell;
        const profitL = netL - total;
        const grossH = b * sellMax;
        const netH = grossH * feeSell;
        const profitH = netH - total;
        const tr = document.createElement("tr");
        tr.classList.add('tr-body-price');
        tr.innerHTML =
            `<td class="td-left td-blocks freeze-col-left">${b}</td>` +
            `<td class="td-center td-cost">${formatCurrency(b * bid)}</td>` +
            `<td class="td-center td-comms">${formatCurrency(comms)}</td>` +
            `<td class="td-center td-total">${formatCurrency(total)}</td>` +
            `<td class="td-center td-sell" data-low="${formatCurrency(netL)}" data-high="${formatCurrency(netH)}">${mode === 'low' ? formatCurrency(netL) : formatCurrency(netH)}</td>` +
            `<td class="td-right td-profit freeze-col-right ${mode === 'low' ? 'profit-min' : 'profit-max'}" data-low="${formatCurrency(profitL)}" data-high="${formatCurrency(profitH)}">${mode === 'low' ? formatCurrency(profitL) : formatCurrency(profitH)}</td>`;        
        tbody.appendChild(tr);
    });
    
    if (frozenL === "frozen") {
        document.querySelectorAll(".freeze-col-left").forEach(td => td.classList.add("frozen"));
    }
    if (frozenR === "frozen") {
        document.querySelectorAll(".freeze-col-right").forEach(td => td.classList.add("frozen"));
    }
}

function renderTableSettings() {
    if (!currentStock || !currentSettings || !currentTicker) return;
    
    // load settings configurations
    const { defaults, modified, modifiedState } = getConfig();
    
    // populate cells
    document.getElementById('td-A1').textContent = formatPercent(defaults.BLOCKAGE_DISCOUNT);
    document.getElementById('td-B1').textContent = formatPercent(defaults.BROKERAGE_FEE);
    document.getElementById('td-C1').textContent = formatPercent(defaults.SELL_MIN);
    document.getElementById('td-D1').textContent = formatPercent(defaults.SELL_MAX);
    document.getElementById('td-A2').textContent = modified.BLOCKAGE_DISCOUNT !== null ? formatPercent(modified.BLOCKAGE_DISCOUNT) : '—';
    document.getElementById('td-B2').textContent = modified.BROKERAGE_FEE     !== null ? formatPercent(modified.BROKERAGE_FEE)     : '—';
    document.getElementById('td-C2').textContent = modified.SELL_MIN          !== null ? formatPercent(modified.SELL_MIN)          : '—';
    document.getElementById('td-D2').textContent = modified.SELL_MAX          !== null ? formatPercent(modified.SELL_MAX)          : '—';
    
    // apply row states
    const defaultRow  = document.getElementById('tr-body-default');
    const modifiedRow = document.getElementById('tr-body-modified');
    
    defaultRow.classList.toggle('enabled', isDefault);
    modifiedRow.classList.toggle('enabled', !isDefault);
    defaultRow.classList.toggle('disabled', false);
    modifiedRow.classList.toggle('disabled', modifiedState === 'null');
    
    const defBtn = document.getElementById('td-btn-default');
    const modBtn = document.getElementById('td-btn-modified');
    if (modifiedState === 'null') {
        defBtn.style.pointerEvents = 'none';
        defBtn.classList.remove('clickable-small');
        modBtn.classList.remove('clickable-small');
        defBtn.classList.add('disabled');
        modBtn.classList.add('disabled');
    } else {
        defBtn.style.pointerEvents = '';
        defBtn.classList.add('clickable-small');
        modBtn.classList.add('clickable-small');
        defBtn.classList.remove('disabled');
        modBtn.classList.remove('disabled');
    }
}

function renderTicker(ticker) {
    const stock = currentStock[ticker];
    if (!stock) throw new Error("ticker not found: " + ticker);
    currentTicker = ticker;
    
    // handle isDefault state for new ticker
    const newModifiedState = getConfig().modifiedState;
    if (isDefault === null) {
        // first load
        isDefault = stock.default !== false;
    } else if (!isDefault && newModifiedState === 'null') {
        // was on modified, but new ticker's modified is disabled — force default
        isDefault = true;
    }
    
    // company and financials shortcuts
    const _C = stock.COMPANY    || {};
    const _F = stock.FINANCIALS || {};
    
    // price and change
    const price     = parseFloat(stock.price) || 0;
    const changeRaw = _F.change && _F.change !== null ? _F.change : 0;
    
    // get active config via getConfig()
    const { active } = getConfig();
    const discPct    = active.BLOCKAGE_DISCOUNT;
    const feePct     = active.BROKERAGE_FEE;
    const feePctSell = active.BROKERAGE_FEE_SELL;
    const sellMinPct = active.SELL_MIN;
    const sellMaxPct = active.SELL_MAX;
    
    // price calculations
    const bid     = fmsRoundPrice(price * (1 - discPct));
    const sellMin = fmsRoundPrice(bid *   (1 + sellMinPct));
    const sellMax = fmsRoundPrice(bid *   (1 + sellMaxPct));
    
    // block calculations
    const feePctMult     = 1 + feePct;
    const blockMinRaw    = DEFAULT_MINIMUM_THRESHOLD / (bid * feePctMult);
    const blockMin       = Math.max(1, fmsRoundShares(blockMinRaw, bid, feePct));
    const blockMinDouble = blockMin * 2;
    const blockMaxHalf   = blockMin * 5;
    const blockMax       = blockMin * 10;
    const blocks         = [blockMax, blockMaxHalf, blockMinDouble, blockMin];
    
    // market update percentages
    const labelBidPct = ((price - bid)   / bid) * 100;
    const labelMinPct = ((sellMin - bid) / bid) * 100;
    const labelMaxPct = ((sellMax - bid) / bid) * 100;
    
    // populate header
    document.getElementById("name").textContent = _C.name || ticker;
    document.getElementById("date").textContent = formatDate(new Date());
    
    // populate market update cards
    document.getElementById("price").textContent        = formatCurrency(price);
    document.getElementById("bid").textContent          = formatCurrency(bid);
    document.getElementById("bid-pct").textContent      = `(-${formatPercent(labelBidPct, false, 0.25)})`;
    document.getElementById("sell-min").textContent     = formatCurrency(sellMin);
    document.getElementById("sell-min-pct").textContent = `(+${formatPercent(labelMinPct, false, 0.5)})`;
    document.getElementById("sell-max").textContent     = formatCurrency(sellMax);
    document.getElementById("sell-max-pct").textContent = `(+${formatPercent(labelMaxPct, false, 0.5)})`;
    
    // change badge
    const change   = formatPercent(changeRaw, false, 0.01);
    const changeEl = document.getElementById("change-pct");
    if (changeRaw) {
        changeEl.textContent = change;
        changeEl.className   = "badge " + (changeRaw < 0 ? "down" : "up");
    } else {
        changeEl.textContent = "";
        changeEl.className   = "badge";
    }
    
    // description
    const desc        = formatDescription(currentStock, ticker);
    const description = desc.d;
    const summary     = desc.s;
    
    // populate information section
    document.getElementById("info-name").textContent      = _C.name     || "";
    document.getElementById("info-ticker").textContent    = _C.ticker   || "";
    document.getElementById("info-exchange").textContent  = _C.exchange || "";
    document.getElementById("info-country").textContent   = _C.country  || "";
    document.getElementById("info-industry").textContent  = _C.industry || "";
    document.getElementById("info-sector").textContent    = _C.sector   || "";
    document.getElementById("info-year").textContent      = _C.year     || "";
    document.getElementById("info-marketCap").textContent = formatCurrency(_F.marketCap, true)            || "";
    document.getElementById("info-desc").textContent      = (fullDesc === "show" ? description : summary) || "";
    document.getElementById("info-weekLow").textContent   = formatCurrency(_F.weekLow)                    || "";
    document.getElementById("info-weekHigh").textContent  = formatCurrency(_F.weekHigh)                   || "";
    
    // show or hide cards based on available data
    toggleCard('info-weekLow', _F.weekLow);
    toggleCard('info-weekHigh', _F.weekHigh);
    
    // website link
    const url  = _C.website || "";
    const link = document.getElementById("info-website");
    link.href  = url;
    link.textContent = formatUrl(url) || "";
    
    // adjust select menu width, render settings and price tables, render news feed and sync price modd
    adjustWidth();
    renderTableSettings();
    renderTablePrice(blocks, bid, feePct, feePctSell, sellMin, sellMax);
    renderNews();
    syncModeUI()
}

// ── LOAD ─────────────────────────────────────────────────
async function loadData() {
    try {
        const [stockRes, settingsRes] = await Promise.all([
            fetch("./data/portfolio.json"),
            fetch("./config/settings.json")
        ]);
        const stockJson = await stockRes.json();
        const settingsJson = await settingsRes.json();

        currentStock = stockJson;
        currentSettings = settingsJson;

        // populate dropdown
        const tickers = Object.keys(stockJson).reverse();
        const tckrSelEl = document.getElementById("ticker-select");
        tckrSelEl.innerHTML = "";
        tickers.forEach(ticker => {
            const opt = document.createElement("option");
            opt.value = ticker;
            opt.textContent = ticker;
            tckrSelEl.appendChild(opt);
        });

        // render first ticker
        renderTicker(tickers[0]);
    } catch (e) {
        document.getElementById("load-error").style.display = "block";
        console.error(e);
    }
}

// ── NEWS ─────────────────────────────────────────────────
function formatNewsDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    }).toUpperCase();
}

function setNewsFilter(f) {
    newsFilter = f;
    document.querySelectorAll('.news-filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.id === `filter-${f}`);
    });
    renderNews();
}

function renderNews() {
    if (!currentStock || !currentTicker) return;

    const stock = currentStock[currentTicker];
    const feed  = stock.NEWS || [];
    const container = document.getElementById('news-feed');
    container.innerHTML = '';

    // sort: freemium first, then by publishDate descending
    const sorted = [...feed].sort((a, b) => {
        if (a.freemium && !b.freemium) return -1;
        if (!a.freemium && b.freemium) return 1;
        return new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime();

        //return new Date(b.publishDate) - new Date(a.publishDate);
    });

    // filter
    const filtered = sorted.filter(item => {
        if (newsFilter === 'all')     return true;
        if (newsFilter === 'public')  return !item.premium;
        if (newsFilter === 'premium') return item.premium;
        return true;
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div class="card row" style="color:var(--text-clr-dim);font-size:0.8rem;">No articles found.</div>';
        return;
    }

    filtered.forEach((item, i) => {
        const card = document.createElement('div');
        const cardId = `news-card-${i}`;

        // determine card type
        let cardClass = 'news-card';
        if (item.freemium) cardClass += ' freemium';
        else if (item.premium) cardClass += ' premium';

        // badge
        let badge = '';
        if (item.freemium)      badge = '<span class="news-badge-freemium">FREE</span>';
        else if (item.premium)  badge = '<span class="news-badge-premium">PREMIUM</span>';

        card.className = cardClass;
        card.innerHTML = `
            <div class="news-card-header">
                <span class="news-card-source">${item.source || ''}${badge ? ' ' + badge : ''}</span>
                <span class="news-card-date">${formatNewsDate(item.publishDate)}</span>
            </div>
            <div class="news-card-title">${item.title}</div>
            <div id="${cardId}-summary" class="news-card-summary">${item.summary}</div>
            <div id="${cardId}-footer" class="news-card-footer">
                <a class="news-card-link clickable-small" href="${item.url}" target="_blank" rel="noopener noreferrer">READ MORE →</a>
            </div>
        `;

        card.addEventListener('click', () => toggleNewsCard(cardId));
        container.appendChild(card);
    });
}

function toggleNewsCard(id) {
    const summary = document.getElementById(`${id}-summary`);
    const footer  = document.getElementById(`${id}-footer`);
    const isOpen  = summary.classList.contains('expanded');

    // close all
    document.querySelectorAll('.news-card-summary').forEach(el => el.classList.remove('expanded'));
    document.querySelectorAll('.news-card-footer').forEach(el => el.classList.remove('visible'));

    // open this one only if it was closed
    if (!isOpen) {
        summary.classList.add('expanded');
        footer.classList.add('visible');
    }
}

// ── TOGGLE ───────────────────────────────────────────────
function switchTicker(ticker) {
    if (!currentStock || !currentSettings) return;
    lockAllDevMode();
    try {
        renderTicker(ticker);
    } catch(e) {
        document.getElementById('load-error').style.display = 'block';
        console.error(e);
    }
}

function setSettings(s) {
    lockAllDevMode();
    const { modifiedState } = getConfig();
    if (!s && modifiedState === 'null') return;
    isDefault = s;
    renderTableSettings();
    // re-render price table with new active config
    const { active }  = getConfig();
    const price       = parseFloat(currentStock[currentTicker].price) || 0;
    const bid         = fmsRoundPrice(price * (1 - active.BLOCKAGE_DISCOUNT));
    const sellMin     = fmsRoundPrice(bid   * (1 + active.SELL_MIN));
    const sellMax     = fmsRoundPrice(bid   * (1 + active.SELL_MAX));
    const feeMult     = 1 + active.BROKERAGE_FEE;
    const blockMinRaw = DEFAULT_MINIMUM_THRESHOLD / (bid * feeMult);
    const blockMin    = Math.max(1, fmsRoundShares(blockMinRaw, bid, active.BROKERAGE_FEE));
    const blocks      = [blockMin * 10, blockMin * 5, blockMin * 2, blockMin];
    renderTablePrice(blocks, bid, active.BROKERAGE_FEE, active.BROKERAGE_FEE_SELL, sellMin, sellMax);
    syncModeUI()
}

function setMode(m) {
    lockAllDevMode();
    mode = m;
    document.getElementById('card-min').classList.toggle('active', m === 'low');
    document.getElementById('card-max').classList.toggle('active', m === 'high');

    // update price table sell/profit cells
    const frozen = document.querySelector('.freeze-col-right.frozen') !== null;
    document.querySelectorAll('.td-sell').forEach(td => {
        td.textContent = td.dataset[m];
    });
    document.querySelectorAll('.td-profit').forEach(td => {
        td.textContent = td.dataset[m];
        // Remove both classes then add the correct one
        td.classList.remove('profit-min', 'profit-max');
        if (m === 'low') {
            td.classList.add('profit-min');
        } else {
            td.classList.add('profit-max');
        }
        // Preserve frozen status if it exists
        if (frozen) {
            td.classList.add('frozen');
        }
    });
}

function toggleCard(id, value) {
    const card = document.getElementById(id).closest(".card");
    card.style.display = value ? "" : "none";
}

function toggleDesc() {
    fullDesc = fullDesc === "show" ? "hide" : "show";
    if (!currentStock || !currentTicker) return;
    const data = formatDescription();
    const text = fullDesc === "show" ? data.d : data.s;
    document.getElementById("info-desc").textContent = text;
}

function toggleFrozenL() {
    frozenL = frozenL === "frozen" ? "" : "frozen";
    const frozen = frozenL !== "";
    if (frozen && frozenR !== "") {
        frozenR = "";
        document.querySelectorAll(".freeze-col-right").forEach(td => {
            td.classList.remove("frozen");
        });
    }
    document.querySelectorAll(".freeze-col-left").forEach(td => {
        td.classList.toggle("frozen", frozen);
    });
}

function toggleFrozenR() {
    frozenR = frozenR === "frozen" ? "" : "frozen";
    const frozen = frozenR !== "";
    if (frozen && frozenL !== "") {
        frozenL = "";
        document.querySelectorAll(".freeze-col-left").forEach(td => {
            td.classList.remove("frozen");
        });
    }
    document.querySelectorAll(".freeze-col-right").forEach(td => {
        td.classList.toggle("frozen", frozen);
    });
}

// ── AUTH ─────────────────────────────────────────────────
function checkPwd() {
    // const pwdVal = document.getElementById("pwd").value;
    const pwdVal = pwdEl.value;
    const gateEl = document.getElementById('gate');
    const contEl = document.getElementById('content');
    const errEl  = document.getElementById('err');
    
    if (pwdVal === PASSWORD) {
        gateEl.style.display = "none";
        contEl.style.display = "block";
        loadData();
    } else {
        errEl.textContent = "incorrect password";
        pwdEl.value = "";
    }
}

// ── LISTENERS ─────────────────────────────────────────────
const detInfoEl = document.getElementById('details-info');
const detNewsEl = document.getElementById('details-news');
const tckrSelEl = document.getElementById('ticker-select');
const pwdEl = document.getElementById('pwd');
const h1El = document.querySelector('h1');
const nameEl = document.getElementById('name');
const priceEl = document.getElementById('price');
const cardMinEl = document.getElementById('card-min');
const cardMaxEl = document.getElementById('card-max');
const detSettingsEl = document.getElementById('details-settings');

if (h1El) {
    h1El.addEventListener('click', handleXerxesFMSTab);
}

if (nameEl) {
    nameEl.addEventListener('click', handleCompanyNameTap);
}

if (priceEl) {
    priceEl.addEventListener('click', handlePriceTap);
}

if (cardMinEl) {
    cardMinEl.addEventListener('click', () => setMode('low'));
}

if (cardMaxEl) {
    cardMaxEl.addEventListener('click', () => setMode('high'));
}

if (detSettingsEl) {
    detSettingsEl.addEventListener('toggle', function() {
        if (this.open) {
            lockAllDevMode();
        }
    });
}

detInfoEl.addEventListener('toggle', function() {
    if (this.open) {
        lockAllDevMode();
    }
    if (!this.open) {
        fullDesc = 'hide';
        if (currentStock && currentTicker) {
            const desc = formatDescription();
            const descEl = document.getElementById('info-desc');
            descEl.textContent = desc.s;
        }
    }
});

detNewsEl.addEventListener('toggle', function() {
    if (this.open) {
        lockAllDevMode();
        renderNews();
    } else {
        // close all expanded cards
        document.querySelectorAll('.news-card-summary').forEach(el => el.classList.remove('expanded'));
        document.querySelectorAll('.news-card-footer').forEach(el => el.classList.remove('visible'));
        // reset scroll position
        const feedEl = document.getElementById('news-feed');
        feedEl.scrollTop = 0;
        // reset all filter
        newsFilter = 'all';
        document.querySelectorAll('.news-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.id === 'filter-all');
        });
    }
});

tckrSelEl.addEventListener('change', adjustWidth);
pwdEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter") checkPwd();
});

// ── TEMP ─────────────────────────────────────────────────



// ALPHA VANTAGE
/*
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
*//*
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
function markKeyAsFailed(apiKey) {
    if (!window.failedKeys) window.failedKeys = new Set();
    window.failedKeys.add(apiKey);
    currentKeyIndex = (currentKeyIndex + 1) % API_KEYS.length;

    Debug.log(`❌ Failed key: ${apiKey}`);
}
*//*
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

            Debug.subgroup('{ Normalization }');
            Debug.log('feed length:', feed.length);

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
*/


