import subprocess
import time
import json
import urllib.request
import base64
import os
import shutil
import asyncio
import websockets
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "report_figures")
os.makedirs(FIG_DIR, exist_ok=True)

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
port = 9335
TEMP_DIR = os.path.join(os.environ.get("TEMP", "."), "chrome_snap_profile2")

def capture_browser_screens():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    cmd = [
        chrome_exe,
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={TEMP_DIR}",
        "--window-size=1650,1150",
        "about:blank"
    ]

    print("Launching headless Chrome for dashboard screenshots...")
    proc = subprocess.Popen(cmd)

    async def run():
        await asyncio.sleep(2)
        tabs = None
        for _ in range(12):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
                    tabs = json.loads(resp.read().decode())
                    break
            except Exception:
                await asyncio.sleep(0.5)

        if not tabs:
            print("Failed to connect to Chrome debugging port")
            return

        page_tabs = [t for t in tabs if t.get("type") == "page"]
        if not page_tabs:
            print("No page tabs found!")
            return

        ws_url = page_tabs[0]["webSocketDebuggerUrl"]
        print("Connected to Chrome Page via DevTools Protocol:", ws_url)

        async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
            async def snap(url, filename, wait_sec=4):
                save_path = os.path.join(FIG_DIR, filename)
                print(f"Navigating to {url}...")
                await ws.send(json.dumps({"id": 10, "method": "Page.navigate", "params": {"url": url}}))
                await asyncio.sleep(wait_sec)
                print(f"Capturing screenshot -> {save_path}...")
                await ws.send(json.dumps({"id": 20, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == 20:
                        data = base64.b64decode(msg["result"]["data"])
                        with open(save_path, "wb") as f:
                            f.write(data)
                        print(f"Saved {filename} ({len(data):,} bytes)")
                        break

            # 1. Full Kubernetes Dashboard Overview (NodePort 30080)
            await snap("http://localhost:30080/", "k8s_dashboard_overview.png", 5)

            # 2. Interactive Drill-Down Dashboard (Electronics category isolated)
            await snap("http://localhost:30080/?drill=Electronics", "k8s_dashboard_drilldown.png", 5)

            # 3. Docker Compose Dashboard (Port 8080)
            await snap("http://localhost:8080/", "docker_dashboard_overview.png", 5)

    try:
        asyncio.run(run())
    finally:
        proc.terminate()
        time.sleep(1)
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        print("Browser screenshots completed.")

def create_terminal_card(title, commands_and_outputs, filename, width=1400):
    """Render authentic command outputs into crisp terminal screenshots."""
    lines = []
    for cmd, out in commands_and_outputs:
        lines.append(("cmd", f"PS C:\\Users\\Rohan\\Desktop\\VA assignment\\7and8> {cmd}"))
        for line in out.splitlines():
            lines.append(("out", line))
        lines.append(("blank", ""))

    font_size = 17
    line_height = 25
    pad_x = 30
    pad_y = 25
    height = 55 + pad_y + len(lines) * line_height + 20

    img = Image.new("RGB", (width, height), color="#070F34")
    draw = ImageDraw.Draw(img)

    try:
        font_mono = ImageFont.truetype("consola.ttf", font_size)
        font_bold = ImageFont.truetype("consolab.ttf", font_size)
    except Exception:
        font_mono = ImageFont.load_default()
        font_bold = font_mono

    # Window titlebar bar
    draw.rectangle([(0, 0), (width, 45)], fill="#0D1B2A")
    draw.line([(0, 45), (width, 45)], fill="#2C3E5A", width=1)

    # Mac/Linux-style window buttons
    draw.ellipse([(20, 16), (32, 28)], fill="#FF007A")
    draw.ellipse([(40, 16), (52, 28)], fill="#FFEA00")
    draw.ellipse([(60, 16), (72, 28)], fill="#00FFB3")

    draw.text((90, 13), f"VeloceAnalytics CLI Terminal — {title}", font=font_bold, fill="#E0E1DD")

    y = 65
    for l_type, l_text in lines:
        if l_type == "blank":
            y += 8
            continue
        elif l_type == "cmd":
            draw.text((pad_x, y), l_text, font=font_bold, fill="#34EDF3")
        elif l_type == "out":
            if any(w in l_text.lower() for w in ["healthy", "running", "bound", "ready"]):
                draw.text((pad_x, y), l_text, font=font_mono, fill="#00FFB3")
            elif any(w in l_text.lower() for w in ["warning", "created", "up-to-date"]):
                draw.text((pad_x, y), l_text, font=font_mono, fill="#FFEA00")
            elif any(w in l_text.lower() for w in ["error", "failed"]):
                draw.text((pad_x, y), l_text, font=font_mono, fill="#FF007A")
            elif any(w in l_text.lower() for w in ["total_revenue_usd", "total_sales", "5840", "3984506.49"]):
                draw.text((pad_x, y), l_text, font=font_bold, fill="#6FFFE9")
            else:
                draw.text((pad_x, y), l_text, font=font_mono, fill="#E0E1DD")
        y += line_height

    out_path = os.path.join(FIG_DIR, filename)
    img.save(out_path, quality=95)
    print(f"Saved terminal capture -> {out_path} ({width}x{height})")

def capture_docker_and_db_screens():
    print("Generating terminal captures for Docker, Kubernetes, and MySQL Database...")

    # 1. Database Queries & Verification
    cmd_mysql1 = 'docker exec va-mysql mysql -u root -ppassword -t -e "SHOW DATABASES;"'
    out_mysql1 = subprocess.check_output(cmd_mysql1, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_mysql2 = 'docker exec va-mysql mysql -u root -ppassword -t -e "USE salesdb; SHOW TABLES; DESCRIBE sales;"'
    out_mysql2 = subprocess.check_output(cmd_mysql2, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_mysql3 = 'docker exec va-mysql mysql -u root -ppassword -t -e "USE salesdb; SELECT COUNT(*) AS total_rows, MIN(date) AS start_date, MAX(date) AS end_date, ROUND(SUM(sales), 2) AS total_revenue_usd, SUM(units) AS total_units FROM sales;"'
    out_mysql3 = subprocess.check_output(cmd_mysql3, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_mysql4 = 'docker exec va-mysql mysql -u root -ppassword -t -e "USE salesdb; SELECT date, region, category, sales, units FROM sales ORDER BY id ASC LIMIT 6;"'
    out_mysql4 = subprocess.check_output(cmd_mysql4, shell=True, text=True, stderr=subprocess.STDOUT)

    create_terminal_card(
        "MySQL 8.0 Relational Database Tier (salesdb.sales Schema & Data Verification)",
        [
            ("docker exec va-mysql mysql -u root -p -t -e \"SHOW DATABASES;\"", out_mysql1),
            ("docker exec va-mysql mysql -u root -p -t -e \"USE salesdb; SHOW TABLES; DESCRIBE sales;\"", out_mysql2),
            ("docker exec va-mysql mysql -u root -p -t -e \"SELECT COUNT(*), MIN(date), MAX(date), SUM(sales), SUM(units) FROM sales;\"", out_mysql3),
            ("docker exec va-mysql mysql -u root -p -t -e \"SELECT * FROM sales ORDER BY id ASC LIMIT 6;\"", out_mysql4),
        ],
        "database_mysql_verification.png"
    )

    # 2. Docker Containers, Images, and Registry Push
    cmd_ps = "docker compose ps"
    out_ps = subprocess.check_output(cmd_ps, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_imgs = 'docker images | Select-String -Pattern "va-"'
    out_imgs = subprocess.check_output(["powershell", "-Command", cmd_imgs], text=True, stderr=subprocess.STDOUT)

    cmd_reg1 = "curl.exe -s http://localhost:5001/v2/_catalog"
    out_reg1 = subprocess.check_output(cmd_reg1, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_reg2 = "curl.exe -s http://localhost:5001/v2/va-frontend/tags/list; curl.exe -s http://localhost:5001/v2/va-backend/tags/list; curl.exe -s http://localhost:5001/v2/va-mysql/tags/list"
    out_reg2 = subprocess.check_output(["powershell", "-Command", cmd_reg2], text=True, stderr=subprocess.STDOUT)

    create_terminal_card(
        "Docker Multi-Container Orchestration & OCI Registry Push",
        [
            ("docker compose ps", out_ps),
            ("docker images | Select-String 'va-'", out_imgs),
            ("curl -s http://localhost:5001/v2/_catalog", out_reg1),
            ("curl -s http://localhost:5001/v2/<repo>/tags/list", out_reg2)
        ],
        "docker_orchestration_registry.png"
    )

    # 3. Kubernetes Deployments, Services, and Inter-Tier Networking
    cmd_k8s1 = "kubectl get pods,svc,pvc,deployments -n va-system -o wide"
    out_k8s1 = subprocess.check_output(cmd_k8s1, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_k8s2 = "curl.exe -s http://localhost:30080/api/health"
    out_k8s2 = subprocess.check_output(cmd_k8s2, shell=True, text=True, stderr=subprocess.STDOUT)

    cmd_k8s3 = "curl.exe -s http://localhost:30080/api/sales/summary"
    out_k8s3 = subprocess.check_output(cmd_k8s3, shell=True, text=True, stderr=subprocess.STDOUT)

    create_terminal_card(
        "Kubernetes Deployments, ClusterIP Services & Ingress Networking",
        [
            ("kubectl get pods,svc,pvc,deployments -n va-system -o wide", out_k8s1),
            ("curl -s http://localhost:30080/api/health", out_k8s2),
            ("curl -s http://localhost:30080/api/sales/summary", out_k8s3)
        ],
        "kubernetes_cluster_services.png"
    )

if __name__ == "__main__":
    capture_browser_screens()
    capture_docker_and_db_screens()
    print("ALL ACTUAL SCREENSHOTS CAPTURED SUCCESSFULLY!")
