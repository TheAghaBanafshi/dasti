#!/usr/bin/env python3
# Cosmetic Wings - Minecraft Java 1.21.11 / Fabric
# No Gradle. Run with Python 3.10+ and JDK 21+.
# The script downloads the toolchain, compiles, remaps and creates CosmeticWings.jar.

import json, os, re, shutil, subprocess, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "CosmeticWings_build"
CACHE = BUILD / "cache"
SRC = BUILD / "src"
CLS = BUILD / "classes"
OUT = ROOT / "CosmeticWings.jar"

MC = "1.21.11"
YARN = "1.21.11+build.6"
LOADER = "0.19.4"
MAVEN = "https://maven.fabricmc.net"
MOJANG_META = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

def log(x): print("[CosmeticWings]", x)

def download(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size:
        return
    log("Downloading " + url)
    urllib.request.urlretrieve(url, path)

def run(cmd):
    log("$ " + " ".join(map(str, cmd)))
    p = subprocess.run(cmd)
    if p.returncode:
        raise SystemExit(p.returncode)

def require_java21():
    if not shutil.which("java") or not shutil.which("javac"):
        raise SystemExit("JDK 21+ is required and must be in PATH.")
    p = subprocess.run(["java", "-version"], capture_output=True)
    s = (p.stdout + p.stderr).decode(errors="ignore")
    m = re.search(r'version "(\d+)', s)
    if not m or int(m.group(1)) < 21:
        raise SystemExit("JDK 21+ is required.")

def write_sources():
    pkg = SRC / "com/example/cosmeticwings"
    mix = pkg / "mixin"
    mix.mkdir(parents=True, exist_ok=True)

    (SRC / "fabric.mod.json").write_text("""{
  "schemaVersion": 1,
  "id": "cosmeticwings",
  "version": "1.0.0",
  "name": "Cosmetic Wings",
  "description": "Cosmetic wings and hats. Open the panel with ]",
  "environment": "client",
  "entrypoints": {
    "client": ["com.example.cosmeticwings.CosmeticWingsClient"]
  },
  "mixins": ["cosmeticwings.mixins.json"],
  "depends": {
    "fabricloader": ">=0.19.0",
    "minecraft": "1.21.11"
  }
}""", encoding="utf-8")

    (SRC / "cosmeticwings.mixins.json").write_text("""{
  "required": true,
  "package": "com.example.cosmeticwings.mixin",
  "compatibilityLevel": "JAVA_21",
  "client": ["MinecraftClientMixin", "PlayerRendererMixin"]
}""", encoding="utf-8")

    (pkg / "CosmeticWingsClient.java").write_text("""package com.example.cosmeticwings;

import net.fabricmc.api.ClientModInitializer;

public final class CosmeticWingsClient implements ClientModInitializer {
    public static int wing = 0;
    public static int hat = 0;

    public static final String[] WINGS = {
        "Angel","Demon","Dragon","Butterfly","Fairy","Phoenix","Crystal","Galaxy",
        "Void","Ender","Amethyst","Flame","Frost","Storm","Solar","Lunar",
        "Neon","Cyber","Steampunk","Mechanical","Feather","Royal","Shadow","Spirit",
        "Aether","Sakura","Emerald","Ruby","Sapphire","Obsidian","Prism","Rainbow",
        "Toxic","Cloud","Star","Comet","Aurora","Inferno","Glacier","Thunder",
        "Ocean","Desert","Nature","Spectral","Ghost","Soul","Cosmic","Ancient",
        "Celestial","Arcane","Butterfly2","Dragon2","Phoenix2","Void2","Prism2"
    };

    public static final String[] HATS = {
        "None","Crown","Halo","Top Hat","Wizard","Cat","Bunny","Creeper",
        "Devil","Angel","King","Queen","Viking","Pirate","Samurai","Ninja",
        "Cowboy","Astronaut","Robot","Duck","Crown2","Halo2","Frost","Flame",
        "Crystal","Ender","Dragon","Fox","Bee","Slime","Sun","Moon"
    };

    @Override
    public void onInitializeClient() {}
}
""", encoding="utf-8")

    (pkg / "CosmeticScreen.java").write_text("""package com.example.cosmeticwings;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class CosmeticScreen extends Screen {
    public CosmeticScreen() { super(Component.literal("Cosmetic Wings")); }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int top = Math.max(28, this.height / 2 - 120);

        this.addRenderableWidget(net.minecraft.client.gui.components.Button.builder(
            Component.literal("Wing: " + CosmeticWingsClient.WINGS[CosmeticWingsClient.wing]),
            b -> {
                CosmeticWingsClient.wing =
                    (CosmeticWingsClient.wing + 1) % CosmeticWingsClient.WINGS.length;
                b.setMessage(Component.literal(
                    "Wing: " + CosmeticWingsClient.WINGS[CosmeticWingsClient.wing]));
            }).bounds(cx - 120, top, 240, 28).build());

        this.addRenderableWidget(net.minecraft.client.gui.components.Button.builder(
            Component.literal("Hat: " + CosmeticWingsClient.HATS[CosmeticWingsClient.hat]),
            b -> {
                CosmeticWingsClient.hat =
                    (CosmeticWingsClient.hat + 1) % CosmeticWingsClient.HATS.length;
                b.setMessage(Component.literal(
                    "Hat: " + CosmeticWingsClient.HATS[CosmeticWingsClient.hat]));
            }).bounds(cx - 120, top + 38, 240, 28).build());

        this.addRenderableWidget(net.minecraft.client.gui.components.Button.builder(
            Component.literal("Close"),
            b -> this.minecraft.setScreen(null)
        ).bounds(cx - 120, top + 76, 240, 28).build());
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float delta) {
        g.fill(0, 0, this.width, this.height, 0xB0101018);
        g.drawCenteredString(this.font, this.title, this.width / 2, 18, 0xFFFFFF);
        g.drawCenteredString(this.font,
            Component.literal("Press ] to reopen  |  Cosmetic only"),
            this.width / 2, this.height - 24, 0xB8C7FF);
        super.render(g, mouseX, mouseY, delta);
    }

    @Override public boolean isPauseScreen() { return false; }
}
""", encoding="utf-8")

    (mix / "MinecraftClientMixin.java").write_text("""package com.example.cosmeticwings.mixin;

import com.example.cosmeticwings.CosmeticScreen;
import net.minecraft.client.Minecraft;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class MinecraftClientMixin {
    private boolean cosmeticwings$lastBracket = false;

    @Inject(method = "tick", at = @At("HEAD"))
    private void cosmeticwings$tick(CallbackInfo ci) {
        Minecraft mc = (Minecraft)(Object)this;
        long handle = mc.getWindow().handle();
        boolean down =
            GLFW.glfwGetKey(handle, GLFW.GLFW_KEY_RIGHT_BRACKET) == GLFW.GLFW_PRESS;

        if (down && !cosmeticwings$lastBracket && mc.screen == null) {
            mc.setScreen(new CosmeticScreen());
        }
        cosmeticwings$lastBracket = down;
    }
}
""", encoding="utf-8")

    (mix / "PlayerRendererMixin.java").write_text("""package com.example.cosmeticwings.mixin;

import com.example.cosmeticwings.CosmeticWingsClient;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(PlayerRenderer.class)
public abstract class PlayerRendererMixin {
    @Inject(method = "render", at = @At("TAIL"))
    private void cosmeticwings$render(
        Object state, PoseStack pose, MultiBufferSource buffers, int light, CallbackInfo ci
    ) {
        VertexConsumer vc = buffers.getBuffer(RenderType.lightning());

        pose.pushPose();
        pose.translate(0.0, 1.0, 0.20);

        int w = CosmeticWingsClient.wing;
        int r = (w * 47 + 90) & 255;
        int g = (w * 83 + 150) & 255;
        int b = (w * 131 + 210) & 255;

        drawWing(vc, pose, -1.0f, r, g, b);
        drawWing(vc, pose,  1.0f, r, g, b);

        if (CosmeticWingsClient.hat != 0) {
            int h = CosmeticWingsClient.hat;
            int hr = (h * 71 + 80) & 255;
            int hg = (h * 43 + 120) & 255;
            int hb = (h * 97 + 160) & 255;
            drawQuad(vc, pose,
                -0.22f,0.58f,-0.10f, 0.22f,0.58f,-0.10f,
                 0.22f,0.58f, 0.10f,-0.22f,0.58f, 0.10f,
                hr,hg,hb);
        }
        pose.popPose();
    }

    private static void drawWing(VertexConsumer v, PoseStack p, float side,
                                 int r, int g, int b) {
        float x0 = side * 0.04f;
        float x1 = side * 0.95f;
        drawQuad(v,p,
            x0,0.00f,0.00f, x1,0.70f,0.00f,
            x1,0.05f,0.06f, x0,0.20f,0.06f, r,g,b);
        drawQuad(v,p,
            x0,0.20f,0.06f, x1,0.05f,0.06f,
            x1,-0.30f,0.02f, x0,0.00f,0.00f, r/2,g/2,b/2);
    }

    private static void drawQuad(VertexConsumer v, PoseStack p,
        float ax,float ay,float az, float bx,float by,float bz,
        float cx,float cy,float cz, float dx,float dy,float dz,
        int r,int g,int b) {
        Matrix4f m = p.last().pose();
        v.addVertex(m,ax,ay,az).setColor(r,g,b,230).setUv(0,0).setLight(0xF000F0).setNormal(0,1,0);
        v.addVertex(m,bx,by,bz).setColor(r,g,b,230).setUv(1,0).setLight(0xF000F0).setNormal(0,1,0);
        v.addVertex(m,cx,cy,cz).setColor(r,g,b,230).setUv(1,1).setLight(0xF000F0).setNormal(0,1,0);
        v.addVertex(m,dx,dy,dz).setColor(r,g,b,230).setUv(0,1).setLight(0xF000F0).setNormal(0,1,0);
    }
}
""", encoding="utf-8")


def main():
    require_java21()
    BUILD.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    write_sources()

    meta = json.loads(urllib.request.urlopen(MOJANG_META).read())
    version = next(v for v in meta["versions"] if v["id"] == MC)
    mc_meta = CACHE / f"{MC}.json"
    download(version["url"], mc_meta)
    data = json.loads(mc_meta.read_text(encoding="utf-8"))

    mcjar = CACHE / f"minecraft-{MC}-client.jar"
    download(data["downloads"]["client"]["url"], mcjar)

    y = YARN.replace("+", "%2B")
    yarn = CACHE / f"yarn-{YARN}-mergedv2.jar"
    download(
        f"{MAVEN}/net/fabricmc/yarn/{y}/yarn-{y}-mergedv2.jar", yarn
    )

    loader = CACHE / f"fabric-loader-{LOADER}.jar"
    download(
        f"{MAVEN}/net/fabricmc/fabric-loader/{LOADER}/fabric-loader-{LOADER}.jar",
        loader,
    )

    # Tiny Remapper has a standalone CLI main class.
    tr = CACHE / "tiny-remapper.jar"
    candidates = [
        f"{MAVEN}/net/fabricmc/tiny-remapper/0.11.3/tiny-remapper-0.11.3-fat.jar",
        f"{MAVEN}/net/fabricmc/tiny-remapper/0.11.3/tiny-remapper-0.11.3.jar",
        f"{MAVEN}/net/fabricmc/tiny-remapper/0.11.2/tiny-remapper-0.11.2-fat.jar",
        f"{MAVEN}/net/fabricmc/tiny-remapper/0.11.2/tiny-remapper-0.11.2.jar",
    ]
    if not tr.exists():
        ok = False
        for url in candidates:
            try:
                log("Trying " + url)
                urllib.request.urlretrieve(url, tr)
                if tr.stat().st_size > 10000:
                    ok = True
                    break
            except Exception:
                if tr.exists(): tr.unlink()
        if not ok:
            raise SystemExit("Tiny Remapper could not be downloaded.")

    # official -> named
    named_mc = CACHE / f"{MC}-named.jar"
    if not named_mc.exists():
        run([
            "java", "-jar", str(tr),
            str(mcjar), str(named_mc), str(yarn),
            "official", "named", str(mcjar),
            "--ignoreConflicts", "--fixPackageAccess"
        ])

    if CLS.exists(): shutil.rmtree(CLS)
    CLS.mkdir(parents=True)

    java_files = [str(f) for f in SRC.rglob("*.java")]
    cp = os.pathsep.join([str(named_mc), str(loader)])
    run([
        "javac", "--release", "21", "-encoding", "UTF-8",
        "-cp", cp, "-d", str(CLS), *java_files
    ])

    named_mod = BUILD / "CosmeticWings-named.jar"
    if named_mod.exists(): named_mod.unlink()
    with zipfile.ZipFile(named_mod, "w", zipfile.ZIP_DEFLATED) as z:
        for f in CLS.rglob("*.class"):
            z.write(f, f.relative_to(CLS).as_posix())
        for f in SRC.rglob("*.json"):
            z.write(f, f.relative_to(SRC).as_posix())

    if OUT.exists(): OUT.unlink()
    # named -> intermediary
    run([
        "java", "-jar", str(tr),
        str(named_mod), str(OUT), str(yarn),
        "named", "intermediary", str(named_mc),
        "--mixin", "--ignoreConflicts", "--fixPackageAccess"
    ])

    print("\nDONE:", OUT)
    print("Minecraft:", MC)
    print("Panel key: ]")
    print("Wing presets: 55")
    print("Hat presets: 32")
    print("Put CosmeticWings.jar in your Fabric mods folder.")


if __name__ == "__main__":
    main()
