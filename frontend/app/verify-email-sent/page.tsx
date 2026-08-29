"use client";

import Link from "next/link";

export default function VerifyEmailSentPage() {
  return (
    <div className="min-h-[calc(100vh-72px)] flex items-center justify-center px-4">
      <div className="w-full max-w-md text-center">
        <div className="w-16 h-16 rounded-full bg-donglyn/20 border border-donglyn/30 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="mail" className="w-8 h-8 text-donglyn" />
        </div>
        <h1 className="text-2xl font-black text-white mb-2">Cek Emailmu</h1>
        <p className="text-white/60 text-sm mb-6">
          Kami telah mengirim link verifikasi ke emailmu. Klik link tersebut untuk активasi akun.
        </p>
        <div className="space-y-3">
          <Link
            href="/login"
            className="block w-full py-3 rounded-full bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition"
          >
            Ke Halaman Login
          </Link>
          <p className="text-white/40 text-xs">
            Tidak menerima email?{" "}
            <button className="text-donglyn hover:underline">Kirim ulang</button>
          </p>
        </div>
      </div>
    </div>
  );
}
