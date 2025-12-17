---
description: Email templates for Magic Link authentication
---

## Better Auth: Magic Link Email Templates

This skill provides email template examples for Magic Link authentication with various providers.

### Prerequisites

- Email provider configured (Resend, SendGrid, Nodemailer)
- React Email (optional, for React-based templates)

### Basic HTML Template

```typescript
// lib/auth.ts
magicLink({
  sendMagicLink: async ({ email, url }) => {
    await sendEmail({
      to: email,
      subject: "Sign in to My App",
      html: `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
          </head>
          <body style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
          ">
            <div style="text-align: center; margin-bottom: 30px;">
              <img src="https://myapp.com/logo.png" alt="My App" width="120">
            </div>

            <h1 style="color: #1a1a1a; font-size: 24px; margin-bottom: 20px;">
              Sign in to My App
            </h1>

            <p style="margin-bottom: 20px;">
              Click the button below to sign in. This link expires in 5 minutes.
            </p>

            <div style="text-align: center; margin: 30px 0;">
              <a href="${url}" style="
                display: inline-block;
                background: #0070f3;
                color: white;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
              ">Sign In</a>
            </div>

            <p style="color: #666; font-size: 14px;">
              If the button doesn't work, copy and paste this link:
            </p>
            <p style="
              color: #0070f3;
              font-size: 12px;
              word-break: break-all;
              background: #f5f5f5;
              padding: 12px;
              border-radius: 4px;
            ">${url}</p>

            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

            <p style="color: #999; font-size: 12px; text-align: center;">
              If you didn't request this email, you can safely ignore it.
            </p>
          </body>
        </html>
      `,
    });
  },
})
```

### React Email Template

```tsx
// emails/magic-link.tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Link,
  Preview,
  Section,
  Text,
} from "@react-email/components";

interface MagicLinkEmailProps {
  url: string;
  appName?: string;
}

export function MagicLinkEmail({
  url,
  appName = "My App",
}: MagicLinkEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Sign in to {appName}</Preview>
      <Body style={main}>
        <Container style={container}>
          <Img
            src="https://myapp.com/logo.png"
            width="120"
            height="40"
            alt={appName}
            style={logo}
          />

          <Heading style={heading}>Sign in to {appName}</Heading>

          <Text style={paragraph}>
            Click the button below to sign in. This link expires in 5 minutes.
          </Text>

          <Section style={buttonContainer}>
            <Button style={button} href={url}>
              Sign In
            </Button>
          </Section>

          <Text style={paragraph}>
            If the button doesn't work, copy and paste this link:
          </Text>

          <Link href={url} style={link}>
            {url}
          </Link>

          <Text style={footer}>
            If you didn't request this email, you can safely ignore it.
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

// Styles
const main = {
  backgroundColor: "#f6f9fc",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const container = {
  backgroundColor: "#ffffff",
  margin: "0 auto",
  padding: "40px",
  borderRadius: "8px",
  maxWidth: "560px",
};

const logo = {
  margin: "0 auto 20px",
  display: "block",
};

const heading = {
  color: "#1a1a1a",
  fontSize: "24px",
  fontWeight: "600",
  textAlign: "center" as const,
  margin: "30px 0",
};

const paragraph = {
  color: "#525252",
  fontSize: "14px",
  lineHeight: "24px",
  textAlign: "center" as const,
};

const buttonContainer = {
  textAlign: "center" as const,
  margin: "30px 0",
};

const button = {
  backgroundColor: "#0070f3",
  borderRadius: "8px",
  color: "#fff",
  fontSize: "16px",
  fontWeight: "600",
  textDecoration: "none",
  textAlign: "center" as const,
  display: "inline-block",
  padding: "14px 32px",
};

const link = {
  color: "#0070f3",
  fontSize: "12px",
  textAlign: "center" as const,
  display: "block",
  wordBreak: "break-all" as const,
};

const footer = {
  color: "#8898aa",
  fontSize: "12px",
  lineHeight: "16px",
  textAlign: "center" as const,
  marginTop: "40px",
};

export default MagicLinkEmail;
```

### Using React Email with Resend

```typescript
// lib/auth.ts
import { Resend } from "resend";
import { render } from "@react-email/render";
import { MagicLinkEmail } from "@/emails/magic-link";

const resend = new Resend(process.env.RESEND_API_KEY);

export const auth = betterAuth({
  plugins: [
    magicLink({
      sendMagicLink: async ({ email, url }) => {
        const html = await render(MagicLinkEmail({ url }));

        await resend.emails.send({
          from: "My App <noreply@myapp.com>",
          to: email,
          subject: "Sign in to My App",
          html,
        });
      },
    }),
  ],
});
```

### Dark Mode Email Template

```tsx
// emails/magic-link-dark.tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Text,
} from "@react-email/components";

interface MagicLinkDarkEmailProps {
  url: string;
}

export function MagicLinkDarkEmail({ url }: MagicLinkDarkEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Sign in to My App</Preview>
      <Body style={main}>
        <Container style={container}>
          <Heading style={heading}>Sign in to My App</Heading>

          <Text style={text}>
            Click below to sign in. This link expires in 5 minutes.
          </Text>

          <Button style={button} href={url}>
            Sign In
          </Button>

          <Text style={footer}>
            If you didn't request this, ignore this email.
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

const main = {
  backgroundColor: "#0a0a0a",
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const container = {
  backgroundColor: "#1a1a1a",
  margin: "40px auto",
  padding: "40px",
  borderRadius: "12px",
  maxWidth: "500px",
  border: "1px solid #333",
};

const heading = {
  color: "#ffffff",
  fontSize: "24px",
  fontWeight: "600",
  textAlign: "center" as const,
  margin: "0 0 20px",
};

const text = {
  color: "#a1a1a1",
  fontSize: "14px",
  textAlign: "center" as const,
  margin: "0 0 30px",
};

const button = {
  backgroundColor: "#ffffff",
  borderRadius: "8px",
  color: "#0a0a0a",
  fontSize: "14px",
  fontWeight: "600",
  textDecoration: "none",
  textAlign: "center" as const,
  display: "block",
  padding: "14px 24px",
  margin: "0 auto",
};

const footer = {
  color: "#666",
  fontSize: "12px",
  textAlign: "center" as const,
  marginTop: "30px",
};

export default MagicLinkDarkEmail;
```

### Minimal Template

```typescript
// Simple text-based email
magicLink({
  sendMagicLink: async ({ email, url }) => {
    await sendEmail({
      to: email,
      subject: "Your sign-in link",
      text: `
Click here to sign in: ${url}

This link expires in 5 minutes.

If you didn't request this, you can ignore this email.
      `.trim(),
      html: `
        <p>Click the link below to sign in:</p>
        <p><a href="${url}">Sign In</a></p>
        <p style="color: #666; font-size: 12px;">
          This link expires in 5 minutes.
        </p>
      `,
    });
  },
})
```

### With Nodemailer

```typescript
import nodemailer from "nodemailer";
import { render } from "@react-email/render";
import { MagicLinkEmail } from "@/emails/magic-link";

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT),
  secure: process.env.SMTP_SECURE === "true",
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

magicLink({
  sendMagicLink: async ({ email, url }) => {
    const html = await render(MagicLinkEmail({ url }));

    await transporter.sendMail({
      from: '"My App" <noreply@myapp.com>',
      to: email,
      subject: "Sign in to My App",
      html,
      text: `Sign in to My App: ${url}`,
    });
  },
})
```

### With SendGrid

```typescript
import sgMail from "@sendgrid/mail";
import { render } from "@react-email/render";
import { MagicLinkEmail } from "@/emails/magic-link";

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

magicLink({
  sendMagicLink: async ({ email, url }) => {
    const html = await render(MagicLinkEmail({ url }));

    await sgMail.send({
      to: email,
      from: "noreply@myapp.com",
      subject: "Sign in to My App",
      html,
      text: `Sign in: ${url}`,
    });
  },
})
```

### Dynamic Template with User Context

```typescript
magicLink({
  sendMagicLink: async ({ email, url }, request) => {
    // Get user agent for context
    const userAgent = request.headers.get("user-agent") || "";
    const isMobile = /mobile/i.test(userAgent);

    await sendEmail({
      to: email,
      subject: "Sign in to My App",
      html: `
        <h1>Sign in to My App</h1>
        <p>You requested to sign in from a ${isMobile ? "mobile device" : "computer"}.</p>
        <a href="${url}" style="
          display: inline-block;
          background: #0070f3;
          color: white;
          padding: ${isMobile ? "16px 40px" : "12px 24px"};
          text-decoration: none;
          border-radius: 8px;
        ">Sign In</a>
      `,
    });
  },
})
```

### Branded Template Generator

```typescript
// lib/email-templates.ts
interface BrandConfig {
  name: string;
  logoUrl: string;
  primaryColor: string;
  supportEmail: string;
}

export function generateMagicLinkEmail(url: string, brand: BrandConfig): string {
  return `
    <!DOCTYPE html>
    <html>
      <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <img src="${brand.logoUrl}" alt="${brand.name}" style="height: 40px; margin: 20px 0;">
        <h1>Sign in to ${brand.name}</h1>
        <a href="${url}" style="
          background: ${brand.primaryColor};
          color: white;
          padding: 14px 28px;
          text-decoration: none;
          border-radius: 6px;
          display: inline-block;
        ">Sign In</a>
        <p style="color: #666; font-size: 12px; margin-top: 40px;">
          Need help? Contact <a href="mailto:${brand.supportEmail}">${brand.supportEmail}</a>
        </p>
      </body>
    </html>
  `;
}

// Usage
magicLink({
  sendMagicLink: async ({ email, url }) => {
    const html = generateMagicLinkEmail(url, {
      name: "My App",
      logoUrl: "https://myapp.com/logo.png",
      primaryColor: "#0070f3",
      supportEmail: "support@myapp.com",
    });

    await sendEmail({ to: email, subject: "Sign in", html });
  },
})
```

### Usage

```
/auth.magicLink.email [template]
```

**User Input**: $ARGUMENTS

Available templates:
- `basic` - Basic HTML template
- `react` - React Email component
- `dark` - Dark mode template
- `minimal` - Simple text/HTML template
- `branded` - Customizable branded template
