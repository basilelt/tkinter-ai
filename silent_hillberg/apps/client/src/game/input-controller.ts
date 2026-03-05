import { clamp, type PlayerInputFrame } from "@silent-hillberg/shared";

interface InputState {
  forward: boolean;
  backward: boolean;
  left: boolean;
  right: boolean;
  jump: boolean;
  sprint: boolean;
  dash: boolean;
  reload: boolean;
  firePrimary: boolean;
  fireSecondary: boolean;
}

const DEFAULT_INPUT: InputState = {
  forward: false,
  backward: false,
  left: false,
  right: false,
  jump: false,
  sprint: false,
  dash: false,
  reload: false,
  firePrimary: false,
  fireSecondary: false
};

export class InputController {
  private readonly state: InputState = { ...DEFAULT_INPUT };
  private readonly keyDownHandler: (event: KeyboardEvent) => void;
  private readonly keyUpHandler: (event: KeyboardEvent) => void;
  private readonly mouseMoveHandler: (event: MouseEvent) => void;
  private readonly mouseDownHandler: (event: MouseEvent) => void;
  private readonly mouseUpHandler: (event: MouseEvent) => void;
  private readonly contextMenuHandler: (event: MouseEvent) => void;

  private enabled = false;
  private pointerLocked = false;
  private yaw = 0;
  private pitch = 0;

  public constructor(private readonly canvas: HTMLCanvasElement, private readonly sensitivity = 0.0021) {
    this.keyDownHandler = (event) => this.handleKey(event, true);
    this.keyUpHandler = (event) => this.handleKey(event, false);
    this.mouseMoveHandler = (event) => this.handleMouseMove(event);
    this.mouseDownHandler = (event) => this.handleMouseButton(event, true);
    this.mouseUpHandler = (event) => this.handleMouseButton(event, false);
    this.contextMenuHandler = (event) => event.preventDefault();

    document.addEventListener("keydown", this.keyDownHandler);
    document.addEventListener("keyup", this.keyUpHandler);
    document.addEventListener("mousemove", this.mouseMoveHandler);
    this.canvas.addEventListener("mousedown", this.mouseDownHandler);
    document.addEventListener("mouseup", this.mouseUpHandler);
    this.canvas.addEventListener("contextmenu", this.contextMenuHandler);

    this.canvas.addEventListener("click", () => {
      if (!this.enabled) {
        return;
      }

      if (!this.pointerLocked) {
        void this.canvas.requestPointerLock();
      }
    });

    document.addEventListener("pointerlockchange", () => {
      this.pointerLocked = document.pointerLockElement === this.canvas;
    });
  }

  public setEnabled(enabled: boolean): void {
    this.enabled = enabled;
    if (!enabled) {
      Object.assign(this.state, DEFAULT_INPUT);
      if (document.pointerLockElement === this.canvas) {
        document.exitPointerLock();
      }
    }
  }

  public setViewAngles(yaw: number, pitch: number): void {
    this.yaw = yaw;
    this.pitch = pitch;
  }

  public buildFrame(seq: number, dtMs: number): PlayerInputFrame {
    let moveX = 0;
    let moveZ = 0;

    if (this.state.left) {
      moveX -= 1;
    }
    if (this.state.right) {
      moveX += 1;
    }
    if (this.state.forward) {
      moveZ += 1;
    }
    if (this.state.backward) {
      moveZ -= 1;
    }

    return {
      seq,
      dtMs: clamp(dtMs, 1, 100),
      moveX,
      moveZ,
      yaw: this.yaw,
      pitch: clamp(this.pitch, -1.45, 1.45),
      jump: this.state.jump,
      sprint: this.state.sprint,
      dash: this.state.dash,
      firePrimary: this.state.firePrimary,
      fireSecondary: this.state.fireSecondary,
      reload: this.state.reload
    };
  }

  public dispose(): void {
    document.removeEventListener("keydown", this.keyDownHandler);
    document.removeEventListener("keyup", this.keyUpHandler);
    document.removeEventListener("mousemove", this.mouseMoveHandler);
    this.canvas.removeEventListener("mousedown", this.mouseDownHandler);
    document.removeEventListener("mouseup", this.mouseUpHandler);
    this.canvas.removeEventListener("contextmenu", this.contextMenuHandler);
  }

  private handleKey(event: KeyboardEvent, pressed: boolean): void {
    if (!this.enabled) {
      return;
    }

    switch (event.code) {
      case "KeyW":
        this.state.forward = pressed;
        break;
      case "KeyS":
        this.state.backward = pressed;
        break;
      case "KeyA":
        this.state.left = pressed;
        break;
      case "KeyD":
        this.state.right = pressed;
        break;
      case "Space":
        this.state.jump = pressed;
        break;
      case "ShiftLeft":
      case "ShiftRight":
        this.state.sprint = pressed;
        break;
      case "KeyQ":
        this.state.dash = pressed;
        break;
      case "KeyR":
        this.state.reload = pressed;
        break;
      default:
        break;
    }
  }

  private handleMouseMove(event: MouseEvent): void {
    if (!this.enabled || !this.pointerLocked) {
      return;
    }

    this.yaw -= event.movementX * this.sensitivity;
    this.pitch -= event.movementY * this.sensitivity;
    this.pitch = clamp(this.pitch, -1.45, 1.45);
  }

  private handleMouseButton(event: MouseEvent, pressed: boolean): void {
    if (!this.enabled) {
      return;
    }

    if (event.button === 0) {
      this.state.firePrimary = pressed;
    }
    if (event.button === 2) {
      this.state.fireSecondary = pressed;
    }
  }
}
