const tg = window.Telegram.WebApp;

// Initialize
tg.expand();
tg.MainButton.hide();

const MOCK_LEADERBOARD = [
    { rank: 1, name: "Priya S.", score: 1450, is_bot: true },
    { rank: 2, name: "Rahul_SSC", score: 1420, is_bot: true },
    { rank: 3, name: "Amit B.", score: 1410, is_bot: true },
    { rank: 4, name: "Sneha K.", score: 1390, is_bot: true },
    { rank: 5, name: "Vikram R.", score: 1380, is_bot: true },
];

function renderLeaderboard() {
    const container = document.getElementById('leaderboard');
    container.innerHTML = ''; // Clear loading

    MOCK_LEADERBOARD.forEach(user => {
        const row = document.createElement('div');
        row.className = 'card p-3 flex items-center justify-between';
        
        // Avatar Initials
        const initials = user.name.slice(0, 2).toUpperCase();
        
        row.innerHTML = `
            <div class="flex items-center">
                <span class="font-bold w-6 text-gray-400">#${user.rank}</span>
                <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold mr-3">
                    ${initials}
                </div>
                <div>
                    <p class="font-medium">${user.name}</p>
                    <p class="text-xs opacity-60">Success Rate: 92%</p>
                </div>
            </div>
            <div class="font-bold text-yellow-400">${user.score}</div>
        `;
        container.appendChild(row);
    });
}

document.getElementById('upgradeBtn').addEventListener('click', () => {
    tg.showPopup({
        title: "👑 Upgrade to PRO",
        message: "Unlock detailed analysis, unlimited quizzes, and beat the competition!",
        buttons: [
            {id: "pay", type: "default", text: "Pay ₹99"},
            {type: "cancel"}
        ]
    }, (btnId) => {
        if (btnId === "pay") {
            // Trigger payment intent via Bot Deep Link
            // Since we are an Inline Web App, sendData doesn't work reliably for bot messages.
            // Deep linking is the standard workaround.
            tg.close();
            tg.openTelegramLink("https://t.me/ElevateAura_Bot?start=subscribe_pro");
        }
    });
});

// Render on load
setTimeout(renderLeaderboard, 500); // Fake network delay
