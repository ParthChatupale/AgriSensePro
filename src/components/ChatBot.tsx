import { useState } from "react";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { askAI } from "@/services/api";
import { toast } from "sonner";

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "Hello! I'm AgriBot. How can I help you today?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { text: userMessage, sender: "user" }]);
    setInput("");
    setIsLoading(true);

    try {
      const aiReply = await askAI(userMessage);
      setMessages((prev) => [...prev, { text: aiReply, sender: "bot" }]);
    } catch (error: any) {
      const errorMessage = error.message || "Failed to get response. Please try again.";
      setMessages((prev) => [...prev, { text: errorMessage, sender: "bot" }]);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-hover bg-secondary hover:bg-secondary/90 animate-float z-50"
        size="icon"
      >
        {isOpen ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>

      {/* Chat Window */}
      {isOpen && (
        <Card className="fixed bottom-24 right-6 w-80 h-96 flex flex-col shadow-hover z-50 bg-card">
          {/* Header */}
          <div className="bg-gradient-hero text-white p-4 rounded-t-lg">
            <h3 className="font-semibold">AgriBot Assistant</h3>
            <p className="text-xs opacity-90">Ask me anything about farming</p>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] px-4 py-2 rounded-lg ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border flex space-x-2">
            <Input
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSend()}
              className="flex-1"
              disabled={isLoading}
            />
            <Button 
              onClick={handleSend} 
              size="icon" 
              className="bg-secondary hover:bg-secondary/90"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </Card>
      )}
    </>
  );
};

export default ChatBot;
