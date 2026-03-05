import { describe, expect, it } from "vitest";
import { guestAuthRequestSchema, playerInputFrameSchema } from "./index";

describe("protocol schemas", () => {
  it("validates guest auth payload", () => {
    const parsed = guestAuthRequestSchema.parse({
      nickname: "Hillberg",
      deviceFingerprint: "abc12345finger"
    });

    expect(parsed.nickname).toBe("Hillberg");
  });

  it("rejects invalid input frame", () => {
    const parsed = playerInputFrameSchema.safeParse({
      seq: -1,
      dtMs: 16,
      moveX: 0,
      moveZ: 0,
      yaw: 0,
      pitch: 0,
      jump: false,
      sprint: false,
      dash: false,
      firePrimary: false,
      fireSecondary: false,
      reload: false
    });

    expect(parsed.success).toBe(false);
  });
});
