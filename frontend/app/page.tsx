import Image from "next/image";
import ChatWidget from "@/components/ChatWidget";

export default function Home() {
  return (
    <main className="relative min-h-screen w-full overflow-hidden font-[family-name:var(--font-geist-sans)]">
      {/* Background Image */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="/campus_bg.png"
          alt="LNMIIT Campus"
          fill
          priority
          className="object-cover object-center"
          quality={100}
        />
        {/* Overlay for readability */}
        <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px]" />
      </div>

      {/* Main Content */}
      <div className="relative flex h-screen flex-col items-center justify-center text-center text-white p-8 space-y-8">
        <div className="animate-fade-in-up space-y-4 max-w-2xl bg-white/10 p-12 rounded-3xl backdrop-blur-md border border-white/20 shadow-2xl">
          <div className="flex justify-center mb-6">
            <div className="bg-white p-4 rounded-2xl shadow-lg">
              <Image src="/logo.png" alt="LNMIIT Logo" width={80} height={80} className="w-20 h-auto" />
            </div>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl drop-shadow-lg">
            Welcome to LNMIIT
          </h1>
          <p className="text-lg sm:text-xl text-gray-200 font-light max-w-lg mx-auto leading-relaxed">
            Your AI-powered assistant is ready to help. Click the button below or the chat icon to get started.
          </p>
        </div>
      </div>

      {/* Chat Widget */}
      <ChatWidget />
    </main>
  );
}
