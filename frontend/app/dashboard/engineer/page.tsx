"use client";

import { useState } from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Terminal, Code, FolderTree } from "lucide-react";
import { motion } from "framer-motion";

export default function EngineerPage() {
    const [activeTab, setActiveTab] = useState<"terminal" | "files">("terminal");
    const [terminalOutput, setTerminalOutput] = useState<string[]>([
        "> System: Engineer Agent initialized.",
        "> Ready for instructions..."
    ]);

    // Mock file tree implementation for now
    const fileTree = [
        { name: "backend", type: "dir", children: ["main.py", "agents/"] },
        { name: "frontend", type: "dir", children: ["app/", "components/"] },
    ];

    return (
        <div className="h-[calc(100vh-2rem)] flex gap-6">
            {/* Left: Chat Interface */}
            <div className="w-1/2 flex flex-col">
                <div className="mb-4">
                    <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
                        <Code className="text-accent" />
                        Engineer
                    </h1>
                    <p className="text-muted-foreground">Your autonomous developer companion.</p>
                </div>

                <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                    <ChatInterface
                        agentName="The Engineer"
                        welcomeMessage="I can modify code, run commands, and debug your project. What shall we build?"
                        endpoint="/engineer/chat"
                        onResponse={(res) => {
                            if (res.metadata?.tool_used) {
                                // Add tool logs to terminal
                                setTerminalOutput(prev => [
                                    ...prev,
                                    `> Agent used tool: ${JSON.stringify(res.metadata)}`
                                ]);
                            }
                        }}
                    />
                </div>
            </div>

            {/* Right: Workspace (Terminal/Files) */}
            <div className="w-1/2 flex flex-col bg-[#1e1e1e] rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
                {/* Tabs */}
                <div className="flex border-b border-white/10 bg-white/5">
                    <button
                        onClick={() => setActiveTab("terminal")}
                        className={`px-4 py-3 flex items-center gap-2 text-sm font-medium transition-colors ${activeTab === "terminal" ? "bg-accent/10 text-accent border-b-2 border-accent" : "text-muted-foreground hover:bg-white/5"
                            }`}
                    >
                        <Terminal size={16} />
                        Terminal
                    </button>
                    <button
                        onClick={() => setActiveTab("files")}
                        className={`px-4 py-3 flex items-center gap-2 text-sm font-medium transition-colors ${activeTab === "files" ? "bg-accent/10 text-accent border-b-2 border-accent" : "text-muted-foreground hover:bg-white/5"
                            }`}
                    >
                        <FolderTree size={16} />
                        Files
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 p-4 font-mono text-sm overflow-auto">
                    {activeTab === "terminal" ? (
                        <div className="space-y-1">
                            {terminalOutput.map((line, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="text-gray-300 break-all"
                                >
                                    <span className="text-green-500 mr-2">$</span>
                                    {line}
                                </motion.div>
                            ))}
                            <div className="animate-pulse text-green-500">_</div>
                        </div>
                    ) : (
                        <div className="text-gray-300">
                            {/* Simple Tree Visualization */}
                            {fileTree.map((item, i) => (
                                <div key={i} className="mb-2">
                                    <div className="flex items-center gap-2 text-blue-400">
                                        <FolderTree size={14} /> {item.name}/
                                    </div>
                                    <div className="pl-6 text-gray-400">
                                        {item.children.map((child, j) => (
                                            <div key={j}>📄 {child}</div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
