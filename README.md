<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>گردونه شانس</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, Segoe UI, sans-serif; }
        body { background: #121212; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; text-align: center; padding: 10px; }
        .container { width: 100%; max-width: 360px; background: #1e1e2f; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { margin-bottom: 10px; font-size: 20px; color: #f39c12; }
        .wheel-container { position: relative; margin: 20px auto; width: 260px; height: 260px; }
        .pointer { position: absolute; top: -15px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 12px solid transparent; border-right: 12px solid transparent; border-top: 22px solid #e74c3c; z-index: 10; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5)); }
        #wheel { width: 100%; height: 100%; border-radius: 50%; border: 5px solid #f39c12; transition: transform 4s cubic-bezier(0.15, 0.99, 0.18, 0.99); }
        button { background: #27ae60; color: #fff; border: none; padding: 12px 30px; font-size: 18px; font-weight: bold; border-radius: 50px; cursor: pointer; transition: 0.3s; margin-top: 15px; width: 100%; }
        button:disabled { background: #555; cursor: not-allowed; }
        .result { margin-top: 15px; font-size: 16px; font-weight: bold; min-height: 24px; color: #2ecc71; }
        .coins { font-size: 18px; margin-top: 10px; color: #f1c40f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>گردونه شانس روزانه</h1>
        <div class="coins">موجودی: <span id="coinCount">0</span> سکه</div>
        <div class="wheel-container">
            <div class="pointer"></div>
            <canvas id="wheel" width="260" height="260"></canvas>
        </div>
        <button id="spinBtn" onclick="spin()">بچرخون!</button>
        <div class="result" id="resultText"></div>
    </div>

    <script>
        const canvas = document.getElementById('wheel');
        const ctx = canvas.getContext('2d');
        const items = ['۱۰ سکه', 'پوچ', '۵۰ سکه', '۵ سکه', '۱۰۰ سکه', 'پوچ', '۲۰ سکه', '۲ برابر'];
        const colors = ['#e74c3c', '#3498db', '#9b59b6', '#f1c40f', '#e67e22', '#1abc9c', '#34495e', '#d35400'];
        let currentRotation = 0;
        let isSpinning = false;
        
        let storedCoins = localStorage.getItem('user_coins');
        let coins = (storedCoins && !isNaN(storedCoins)) ? parseInt(storedCoins) : 0;

        function updateCoinDisplay() {
            document.getElementById('coinCount').innerText = coins;
        }
        updateCoinDisplay();

        function drawWheel() {
            const numSegments = items.length;
            const anglePerSegment = (2 * Math.PI) / numSegments;
            for (let i = 0; i < numSegments; i++) {
                ctx.beginPath();
                ctx.fillStyle = colors[i];
                ctx.moveTo(130, 130);
                ctx.arc(130, 130, 130, i * anglePerSegment, (i + 1) * anglePerSegment);
                ctx.fill();
                ctx.save();
                ctx.translate(130, 130);
                ctx.rotate(i * anglePerSegment + anglePerSegment / 2);
                ctx.textAlign = "right";
                ctx.fillStyle = "#fff";
                ctx.font = "bold 13px Tahoma";
                ctx.fillText(items[i], 110, 5);
                ctx.restore();
            }
        }
        drawWheel();

        function playSound(freq, duration) {
            try {
                const ctxAudio = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctxAudio.createOscillator();
                osc.frequency.value = freq;
                osc.connect(ctxAudio.destination);
                osc.start();
                osc.stop(ctxAudio.currentTime + duration);
            } catch(e){}
        }

        function spin() {
            if (isSpinning) return;
            isSpinning = true;
            document.getElementById('spinBtn').disabled = true;
            document.getElementById('resultText').innerText = 'در حال چرخش...';

            const extraDegrees = Math.floor(Math.random() * 360) + 1440;
            currentRotation += extraDegrees;
            canvas.style.transform = `rotate(${currentRotation}deg)`;

            playSound(400, 0.2);

            setTimeout(() => {
                isSpinning = false;
                document.getElementById('spinBtn').disabled = false;
                
                const actualDegrees = currentRotation % 360;
                const segmentAngle = 360 / items.length;
                const index = Math.floor((360 - (actualDegrees % 360) + 270) % 360 / segmentAngle);
                const prize = items[index];

                document.getElementById('resultText').innerText = `برنده شدید: ${prize}`;
                playSound(800, 0.4);

                if (prize.includes('سکه')) {
                    const amount = parseInt(prize.replace(/[^\d]/g, '')) || 0;
                    coins += amount;
                } else if (prize === '۲ برابر') {
                    coins = coins > 0 ? coins * 2 : 10;
                }
                
                localStorage.setItem('user_coins', coins);
                updateCoinDisplay();
            }, 4000);
        }
    </script>
</body>
</html>
