import * as THREE from "three";
import type { GameSnapshot, NetEnemyState, NetPlayerState } from "@silent-hillberg/shared";

const ENEMY_ASSETS = [
  "cyril_maigreur.jpeg",
  "hassen.jpg",
  "jw2.jpeg",
  "jw3.jpg",
  "jw4.webp",
  "perronne.jpeg",
  "le_chat_mange_la_souris.webp",
  "JW.png"
] as const;

export class WorldRenderer {
  private readonly scene: THREE.Scene;
  private readonly camera: THREE.PerspectiveCamera;
  private readonly renderer: THREE.WebGLRenderer;
  private readonly textureLoader: THREE.TextureLoader;

  private readonly enemyTextures = new Map<string, THREE.Texture>();
  private readonly enemySprites = new Map<string, THREE.Sprite>();
  private readonly remotePlayers = new Map<string, THREE.Mesh>();
  private readonly remotePlayerTargets = new Map<string, THREE.Vector3>();
  private readonly enemyTargets = new Map<string, THREE.Vector3>();
  private readonly projectileMeshes = new Map<string, THREE.Mesh>();

  private readonly extractionMesh: THREE.Mesh;
  private readonly extractionRing: THREE.LineLoop;
  private readonly gunMesh: THREE.Mesh;

  private readonly remotePlayerMaterial: THREE.MeshBasicMaterial;

  public constructor(private readonly canvas: HTMLCanvasElement) {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x5f6772);
    this.scene.fog = new THREE.FogExp2(0x9ca5b2, 0.022);

    this.camera = new THREE.PerspectiveCamera(77, canvas.clientWidth / canvas.clientHeight, 0.1, 250);
    this.camera.rotation.order = "YXZ";

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: "high-performance"
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.95;

    this.textureLoader = new THREE.TextureLoader();

    for (const asset of ENEMY_ASSETS) {
      const texture = this.textureLoader.load(`/assets/${asset}`);
      texture.colorSpace = THREE.SRGBColorSpace;
      this.enemyTextures.set(asset, texture);
    }

    const playerTexture = this.textureLoader.load("/assets/joueur.jpeg");
    playerTexture.colorSpace = THREE.SRGBColorSpace;
    this.remotePlayerMaterial = new THREE.MeshBasicMaterial({
      map: playerTexture,
      transparent: false,
      side: THREE.DoubleSide
    });

    this.buildEnvironment();

    const extractionGeometry = new THREE.CylinderGeometry(8, 8, 0.15, 48, 1, true);
    const extractionMaterial = new THREE.MeshBasicMaterial({
      color: 0x64f06d,
      transparent: true,
      opacity: 0.22,
      side: THREE.DoubleSide
    });
    this.extractionMesh = new THREE.Mesh(extractionGeometry, extractionMaterial);
    this.extractionMesh.position.set(0, 0.08, 58);
    this.extractionMesh.visible = false;

    const ringPoints: THREE.Vector3[] = [];
    const radius = 8;
    for (let step = 0; step < 64; step += 1) {
      const angle = (step / 64) * Math.PI * 2;
      ringPoints.push(new THREE.Vector3(Math.cos(angle) * radius, 0.2, Math.sin(angle) * radius));
    }
    this.extractionRing = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints(ringPoints),
      new THREE.LineBasicMaterial({ color: 0x89ff95, transparent: true, opacity: 0.55 })
    );
    this.extractionRing.position.copy(this.extractionMesh.position);
    this.extractionRing.visible = false;

    this.scene.add(this.extractionMesh, this.extractionRing);

    this.gunMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.24, 0.16, 0.62),
      new THREE.MeshStandardMaterial({
        color: 0x22252e,
        metalness: 0.2,
        roughness: 0.4
      })
    );
    this.gunMesh.position.set(0.28, -0.3, -0.66);
    this.camera.add(this.gunMesh);
    this.scene.add(this.camera);

    window.addEventListener("resize", () => this.handleResize());
    this.handleResize();
  }

  public render(snapshot: GameSnapshot | null, localPlayerId: string | null): void {
    if (snapshot && localPlayerId) {
      this.syncPlayers(snapshot.players, localPlayerId);
      this.syncEnemies(snapshot.enemies);
      this.syncProjectiles(snapshot);
      this.syncExtraction(snapshot);

      const localPlayer = snapshot.players.find((player) => player.id === localPlayerId);
      if (localPlayer) {
        this.camera.position.set(localPlayer.position.x, localPlayer.position.y + 1.62, localPlayer.position.z);
        this.camera.rotation.y = localPlayer.yaw;
        this.camera.rotation.x = localPlayer.pitch;
      }
    }

    for (const mesh of this.remotePlayers.values()) {
      mesh.lookAt(this.camera.position.x, mesh.position.y, this.camera.position.z);
    }

    for (const sprite of this.enemySprites.values()) {
      sprite.lookAt(this.camera.position);
    }

    this.renderer.render(this.scene, this.camera);
  }

  public dispose(): void {
    this.renderer.dispose();
  }

  private handleResize(): void {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    this.camera.aspect = width / Math.max(1, height);
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height, false);
  }

  private buildEnvironment(): void {
    const ambient = new THREE.AmbientLight(0x9ca6b8, 0.48);
    this.scene.add(ambient);

    const moon = new THREE.DirectionalLight(0xd7e1ff, 0.56);
    moon.position.set(8, 17, -5);
    this.scene.add(moon);

    const fogLamp = new THREE.PointLight(0xeff5ff, 1.1, 28, 1.35);
    fogLamp.position.set(0, 5.5, 15);
    this.scene.add(fogLamp);

    const floorTexture = this.textureLoader.load("/assets/scala_mayo.jpg");
    floorTexture.colorSpace = THREE.SRGBColorSpace;
    floorTexture.wrapS = THREE.RepeatWrapping;
    floorTexture.wrapT = THREE.RepeatWrapping;
    floorTexture.repeat.set(18, 18);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(280, 280),
      new THREE.MeshStandardMaterial({
        map: floorTexture,
        color: 0x8a9098,
        roughness: 0.97,
        metalness: 0.02
      })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = 0;
    this.scene.add(ground);

    const buildingMaterial = new THREE.MeshStandardMaterial({
      color: 0x272d38,
      roughness: 0.87,
      metalness: 0.08
    });

    const wingA = new THREE.Mesh(new THREE.BoxGeometry(48, 14, 18), buildingMaterial);
    wingA.position.set(-18, 7, -26);

    const wingB = new THREE.Mesh(new THREE.BoxGeometry(44, 10, 16), buildingMaterial);
    wingB.position.set(18, 5, -20);

    const hall = new THREE.Mesh(new THREE.BoxGeometry(30, 9, 24), buildingMaterial);
    hall.position.set(2, 4.5, -45);

    this.scene.add(wingA, wingB, hall);

    const signTexture = this.textureLoader.load("/assets/silent_hillberg.png");
    signTexture.colorSpace = THREE.SRGBColorSpace;
    const sign = new THREE.Mesh(
      new THREE.PlaneGeometry(20, 8),
      new THREE.MeshBasicMaterial({ map: signTexture, transparent: true })
    );
    sign.position.set(0, 11, -16);
    this.scene.add(sign);

    const billboardTexture = this.textureLoader.load("/assets/scala_mayo.jpg");
    billboardTexture.colorSpace = THREE.SRGBColorSpace;
    const infoBoard = new THREE.Mesh(
      new THREE.PlaneGeometry(8, 10),
      new THREE.MeshBasicMaterial({ map: billboardTexture })
    );
    infoBoard.position.set(-32, 5, 6);
    infoBoard.rotation.y = Math.PI / 4;
    this.scene.add(infoBoard);

    for (let index = 0; index < 12; index += 1) {
      const pole = new THREE.Mesh(
        new THREE.CylinderGeometry(0.12, 0.15, 2.7, 8),
        new THREE.MeshStandardMaterial({ color: 0x2d3139, roughness: 0.75 })
      );
      const x = -42 + index * 7.6;
      pole.position.set(x, 1.35, 18 + Math.sin(index * 0.6) * 2);
      this.scene.add(pole);
    }
  }

  private syncPlayers(players: NetPlayerState[], localPlayerId: string): void {
    const activeIds = new Set<string>();

    for (const player of players) {
      if (!player.alive) {
        continue;
      }

      activeIds.add(player.id);

      if (player.id === localPlayerId) {
        continue;
      }

      let mesh = this.remotePlayers.get(player.id);
      if (!mesh) {
        mesh = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.8), this.remotePlayerMaterial.clone());
        mesh.position.set(player.position.x, player.position.y + 1, player.position.z);
        this.remotePlayers.set(player.id, mesh);
        this.remotePlayerTargets.set(player.id, new THREE.Vector3(player.position.x, player.position.y + 1, player.position.z));
        this.scene.add(mesh);
      }

      const target = this.remotePlayerTargets.get(player.id);
      if (!target) {
        continue;
      }

      target.set(player.position.x, player.position.y + 1, player.position.z);
      mesh.position.lerp(target, 0.35);
    }

    for (const [id, mesh] of this.remotePlayers.entries()) {
      if (activeIds.has(id)) {
        continue;
      }

      this.scene.remove(mesh);
      this.remotePlayers.delete(id);
      this.remotePlayerTargets.delete(id);
    }
  }

  private syncEnemies(enemies: NetEnemyState[]): void {
    const activeIds = new Set<string>();

    for (const enemy of enemies) {
      if (!enemy.alive) {
        continue;
      }

      activeIds.add(enemy.id);

      let sprite = this.enemySprites.get(enemy.id);
      if (!sprite) {
        const texture = this.enemyTextures.get(enemy.spriteAsset) ?? this.enemyTextures.get("hassen.jpg");
        if (!texture) {
          continue;
        }

        const material = new THREE.SpriteMaterial({
          map: texture,
          transparent: true,
          alphaTest: 0.08
        });

        sprite = new THREE.Sprite(material);
        this.enemySprites.set(enemy.id, sprite);
        this.enemyTargets.set(enemy.id, new THREE.Vector3(enemy.position.x, enemy.position.y + 1.25, enemy.position.z));
        this.scene.add(sprite);
      }

      const baseScale = enemy.elite ? 5.6 : 2.4;
      sprite.scale.set(baseScale, baseScale, baseScale);

      const target = this.enemyTargets.get(enemy.id);
      if (!target) {
        continue;
      }
      target.set(enemy.position.x, enemy.position.y + baseScale * 0.25, enemy.position.z);
      sprite.position.lerp(target, 0.4);
    }

    for (const [enemyId, sprite] of this.enemySprites.entries()) {
      if (activeIds.has(enemyId)) {
        continue;
      }

      this.scene.remove(sprite);
      this.enemySprites.delete(enemyId);
      this.enemyTargets.delete(enemyId);
    }
  }

  private syncProjectiles(snapshot: GameSnapshot): void {
    const activeIds = new Set<string>();

    for (const projectile of snapshot.projectiles) {
      activeIds.add(projectile.id);

      let mesh = this.projectileMeshes.get(projectile.id);
      if (!mesh) {
        mesh = new THREE.Mesh(
          new THREE.SphereGeometry(0.1, 10, 10),
          new THREE.MeshStandardMaterial({
            color: 0xffad4a,
            emissive: 0xff7a14,
            emissiveIntensity: 0.6,
            roughness: 0.22
          })
        );
        this.projectileMeshes.set(projectile.id, mesh);
        this.scene.add(mesh);
      }

      mesh.position.set(projectile.position.x, projectile.position.y, projectile.position.z);
    }

    for (const [projectileId, mesh] of this.projectileMeshes.entries()) {
      if (activeIds.has(projectileId)) {
        continue;
      }

      this.scene.remove(mesh);
      this.projectileMeshes.delete(projectileId);
    }
  }

  private syncExtraction(snapshot: GameSnapshot): void {
    this.extractionMesh.visible = snapshot.extraction.active;
    this.extractionRing.visible = snapshot.extraction.active;

    this.extractionMesh.position.set(snapshot.extraction.center.x, 0.08, snapshot.extraction.center.z);
    this.extractionRing.position.set(snapshot.extraction.center.x, 0.2, snapshot.extraction.center.z);

    const ratio = Math.max(0, Math.min(1, snapshot.extraction.progress / Math.max(1, snapshot.extraction.requiredProgress)));

    const extractionMaterial = this.extractionMesh.material as THREE.MeshBasicMaterial;
    extractionMaterial.opacity = 0.18 + ratio * 0.45;

    const ringMaterial = this.extractionRing.material as THREE.LineBasicMaterial;
    ringMaterial.opacity = 0.25 + ratio * 0.75;
  }
}
