/**
 * RCCM学習アプリ - シンプル化されたモバイル機能 JavaScript
 * PWA、オフライン、タッチ操作（音声機能削除版）
 */

class MobileFeatures {
    constructor() {
        this.isOnline = navigator.onLine;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchStartTime = 0;

        this.init();
    }

    init() {
        this.setupPWA();
        this.setupOfflineHandler();
        this.setupTouchGestures();
        this.setupKeyboardShortcuts();
        this.setupPerformanceMonitoring();
        this.setupAccessibilityFeatures();
        this.setupErrorBoundary();

        console.log('Simplified mobile features initialized');
    }

    // PWA機能の設定
    setupPWA() {
        // Service Workerの登録
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);

                    // 更新チェック
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                this.showUpdateAvailable();
                            }
                        });
                    });
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }

        // インストール促進
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton(deferredPrompt);
        });
    }

    // オフライン機能の設定
    setupOfflineHandler() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateConnectionStatus();
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateConnectionStatus();
        });

        this.updateConnectionStatus();
    }

    // タッチジェスチャーの設定
    setupTouchGestures() {
        if (!('ontouchstart' in window)) return;

        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
            this.touchStartTime = Date.now();
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (e.touches.length > 0) return;

            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const touchTime = Date.now() - this.touchStartTime;

            if (touchTime > 500) return; // 長すぎるタッチは無視

            const deltaX = touchEndX - this.touchStartX;
            const deltaY = touchEndY - this.touchStartY;
            const absDeltaX = Math.abs(deltaX);
            const absDeltaY = Math.abs(deltaY);

            if (absDeltaX > 50 && absDeltaX > absDeltaY * 2) {
                if (deltaX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
        }, { passive: true });
    }

    // キーボードショートカットの設定
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd キーとの組み合わせは無視
            if (e.ctrlKey || e.metaKey) return;

            switch(e.code) {
                case 'Digit1':
                case 'Digit2':
                case 'Digit3':
                case 'Digit4':
                    if (!e.shiftKey && !e.altKey) {
                        this.selectAnswer(e.code.slice(-1));
                        e.preventDefault();
                    }
                    break;
                case 'Enter':
                    this.submitAnswer();
                    e.preventDefault();
                    break;
                case 'KeyN':
                    if (e.shiftKey) {
                        this.nextQuestion();
                        e.preventDefault();
                    }
                    break;
                case 'KeyP':
                    if (e.shiftKey) {
                        this.previousQuestion();
                        e.preventDefault();
                    }
                    break;
            }
        });
    }

    // パフォーマンス監視
    setupPerformanceMonitoring() {
        // ページロード時間の記録
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);

            // 遅い場合は警告
            if (loadTime > 3000) {
                console.warn('Page load time is slow');
            }
        });

        // メモリ使用量の監視（対応ブラウザのみ）
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > 50 * 1024 * 1024) { // 50MB
                    console.warn('High memory usage detected');
                }
            }, 30000);
        }
    }

    // アクセシビリティ機能
    setupAccessibilityFeatures() {
        // フォーカス管理
        this.setupFocusManagement();

        // ハイコントラストモード検出
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }

        // 動きの削減設定検出
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('reduced-motion');
        }
    }

    // エラーバウンダリ
    setupErrorBoundary() {
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.reportError(e.error);
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.reportError(e.reason);
        });
    }

    // ユーティリティメソッド
    showUpdateAvailable() {
        const updateBanner = document.createElement('div');
        updateBanner.className = 'alert alert-info fixed-top';
        updateBanner.innerHTML = `
            <div class="container">
                新しいバージョンが利用可能です。
                <button class="btn btn-sm btn-primary ms-2" onclick="location.reload()">更新</button>
            </div>
        `;
        document.body.appendChild(updateBanner);
    }

    showInstallButton(deferredPrompt) {
        // インストールボタンを表示する処理
        console.log('Install prompt available');
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = this.isOnline ? 'オンライン' : 'オフライン';
            statusElement.className = this.isOnline ? 'text-success' : 'text-warning';
        }
    }

    syncOfflineData() {
        // オフラインデータの同期処理
        console.log('Syncing offline data...');
    }

    handleSwipeLeft() {
        this.nextQuestion();
    }

    handleSwipeRight() {
        this.previousQuestion();
    }

    selectAnswer(number) {
        const answerButton = document.querySelector(`input[value="${String.fromCharCode(64 + parseInt(number))}"]`);
        if (answerButton) {
            answerButton.checked = true;
            answerButton.dispatchEvent(new Event('change'));
        }
    }

    submitAnswer() {
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.click();
        }
    }

    nextQuestion() {
        const nextButton = document.querySelector('a[href*="next"], button:contains("次")');
        if (nextButton) {
            nextButton.click();
        }
    }

    previousQuestion() {
        const prevButton = document.querySelector('a[href*="prev"], button:contains("前")');
        if (prevButton) {
            prevButton.click();
        }
    }

    setupFocusManagement() {
        // タブキー利用者のためのフォーカス表示
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }

    reportError(error) {
        // エラー報告機能（必要に応じて実装）
        console.error('Reported error:', error);
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    window.mobileFeatures = new MobileFeatures();
});