import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DevCanvas",
  description: "개발자 중심 AI UI 설계/구현 플랫폼",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
