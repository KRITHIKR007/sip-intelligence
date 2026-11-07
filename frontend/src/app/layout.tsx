import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '@/components/layout/AppShell';

export const metadata: Metadata = {
  title: 'SIP Intelligence | Railway Signalling & Interlocking Intelligence Platform',
  description: 'Multimodal Railway Signalling Plan Intelligence, Retrieval and Validation Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Unregister any legacy service workers (e.g. from previous projects on localhost:3000)
              if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
                navigator.serviceWorker.getRegistrations().then(function(registrations) {
                  for (var i = 0; i < registrations.length; i++) {
                    registrations[i].unregister();
                  }
                });
                if ('caches' in window) {
                  caches.keys().then(function(names) {
                    for (var i = 0; i < names.length; i++) {
                      caches.delete(names[i]);
                    }
                  });
                }
              }
            `,
          }}
        />
      </head>
      <body className="bg-slate-50 text-slate-900">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
