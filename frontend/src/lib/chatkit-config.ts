import type { ColorScheme, StartScreenPrompt, ThemeOption } from "@openai/chatkit-react";

export const WORKFLOW_ID =
  process.env.NEXT_PUBLIC_CHATKIT_WORKFLOW_ID?.trim() ?? "";

export const CREATE_SESSION_ENDPOINT = "/api/create-session";

export const STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "What can you do?",
    prompt: "What can you do?",
    icon: "circle-question",
  },
  {
    label: "Add a new task",
    prompt: "Add a task to buy groceries tomorrow",
    icon: "document",
  },
  {
    label: "Show my tasks",
    prompt: "Show me all my tasks",
    icon: "document",
  },
  {
    label: "Mark task complete",
    prompt: "Mark my first task as complete",
    icon: "agent",
  },
];

export const PLACEHOLDER_INPUT = "Ask me to manage your tasks...";

export const GREETING = "Hello! I'm your AI Task Assistant. How can I help you today?";

export const getThemeConfig = (theme: ColorScheme): ThemeOption => ({
  colorScheme: theme,
  color: {
    grayscale: {
      hue: 220,
      tint: 6,
      shade: theme === "dark" ? -1 : -4,
    },
    accent: {
      primary: theme === "dark" ? "#f1f5f9" : "#0f172a",
      level: 1,
    },
    surface: {
      background: theme === "dark" ? "#0f172a" : "#f8fafc",
      foreground: theme === "dark" ? "#1e293b" : "#ffffff",
    },
  },
  radius: "round",
  density: "normal",
  typography: {
    baseSize: 16,
  },
});
