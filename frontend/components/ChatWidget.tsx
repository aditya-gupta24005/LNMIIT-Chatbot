"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Bot, User, Minimize2 } from "lucide-react";
import clsx from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

interface Message {
    role: "user" | "bot";
    content: string;
}

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const toggleChat = () => setIsOpen(!isOpen);

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!inputValue.trim()) return;

        const userMsg = inputValue.trim();
        setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
        setInputValue("");
        setIsLoading(true);

        try {
            const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000/chat";
            const res = await fetch(backendUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userMsg }),
            });

            if (!res.ok) throw new Error("Network response was not ok");

            const data = await res.json();
            setMessages((prev) => [...prev, { role: "bot", content: data.response || "No response received." }]);
        } catch (error) {
            console.error("Error:", error);
            setMessages((prev) => [...prev, { role: "bot", content: "⚠️ Sorry, I couldn't connect to the server." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <AnimatePresence>
                {!isOpen && (
                    <motion.button
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={toggleChat}
                        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-full bg-blue-600 px-6 py-4 text-white shadow-lg shadow-blue-600/30 backdrop-blur-sm transition-colors hover:bg-blue-700"
                    >
                        <MessageCircle className="h-6 w-6" />
                        <span className="font-semibold">Ask LNMIIT</span>
                    </motion.button>
                )}
            </AnimatePresence>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="fixed bottom-6 right-6 z-50 flex h-[600px] w-[380px] flex-col overflow-hidden rounded-2xl border border-white/20 bg-white/80 shadow-2xl backdrop-blur-xl dark:bg-slate-900/80"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between bg-blue-600 px-4 py-3 text-white">
                            <div className="flex items-center gap-2">
                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white p-1">
                                    <img src="/logo.png" alt="Logo" className="h-full w-full object-contain" />
                                </div>
                                <h3 className="text-sm font-bold tracking-wide">LNMIIT Assistant</h3>
                            </div>
                            <button
                                onClick={toggleChat}
                                className="rounded-full p-1 hover:bg-white/20 transition-colors"
                                aria-label="Close chat"
                            >
                                <Minimize2 className="h-5 w-5" />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-gray-300">
                            {messages.length === 0 ? (
                                <div className="flex h-full flex-col items-center justify-center text-center text-gray-500">
                                    <span className="mb-2 text-4xl">👋</span>
                                    <p className="font-medium">Welcome to LNMIIT!</p>
                                    <p className="text-xs">How can I help you today?</p>
                                </div>
                            ) : (
                                <div className="flex flex-col gap-3">
                                    {messages.map((msg, idx) => (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className={cn(
                                                "flex w-max max-w-[85%] flex-col rounded-2xl px-4 py-2 text-sm shadow-sm",
                                                msg.role === "user"
                                                    ? "self-end rounded-br-none bg-blue-600 text-white"
                                                    : "self-start rounded-bl-none bg-white text-gray-800 dark:bg-slate-800 dark:text-gray-100"
                                            )}
                                        >
                                            {msg.content}
                                        </motion.div>
                                    ))}
                                    {isLoading && (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="self-start rounded-2xl rounded-bl-none bg-white px-4 py-2 text-xs text-gray-500 shadow-sm dark:bg-slate-800"
                                        >
                                            <span className="animate-pulse">Thinking...</span>
                                        </motion.div>
                                    )}
                                    <div ref={messagesEndRef} />
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <form
                            onSubmit={handleSubmit}
                            className="border-t border-gray-200 bg-white/50 p-3 backdrop-blur-md dark:border-gray-700 dark:bg-slate-900/50"
                        >
                            <div className="relative flex items-center">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    placeholder="Type your query..."
                                    className="w-full rounded-full border border-gray-300 bg-white py-2.5 pl-4 pr-12 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-slate-800 dark:text-white"
                                />
                                <button
                                    type="submit"
                                    disabled={!inputValue.trim() || isLoading}
                                    className="absolute right-1.5 top-1.5 flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white transition-transform hover:scale-105 disabled:bg-gray-400 disabled:hover:scale-100"
                                >
                                    <Send className="h-4 w-4" />
                                </button>
                            </div>
                        </form>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
