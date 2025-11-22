import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Mail, Phone, MapPin } from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";

const Contact = () => {
  const { t } = useTranslation();
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success(t("contact.success"));
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-heading font-bold text-primary mb-4">{t("contact.title")}</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {t("contact.subtitle")}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <Card className="p-6 text-center hover:shadow-hover transition-all bg-gradient-card">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Mail className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">{t("contact.email_title")}</h3>
            <p className="text-sm text-muted-foreground">support@krushiRakshak.com</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-hover transition-all bg-gradient-card">
            <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center mx-auto mb-4">
              <Phone className="h-6 w-6 text-secondary" />
            </div>
            <h3 className="font-semibold mb-2">{t("contact.call_title")}</h3>
            <p className="text-sm text-muted-foreground">+91 91680-123-XXXX</p>
          </Card>

          <Card className="p-6 text-center hover:shadow-hover transition-all bg-gradient-card">
            <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
              <MapPin className="h-6 w-6 text-accent" />
            </div>
            <h3 className="font-semibold mb-2">{t("contact.visit_title")}</h3>
            <p className="text-sm text-muted-foreground">Nashik, Maharashtra</p>
          </Card>
        </div>

        <Card className="p-8 shadow-hover bg-gradient-card max-w-2xl mx-auto">
          <h2 className="text-2xl font-heading font-bold mb-6">{t("contact.form_title")}</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">{t("contact.name")}</Label>
                <Input id="name" placeholder={t("contact.name_placeholder")} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">{t("contact.email")}</Label>
                <Input id="email" type="email" placeholder={t("contact.email_placeholder")} required />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">{t("contact.subject")}</Label>
              <Input id="subject" placeholder={t("contact.subject_placeholder")} required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">{t("contact.message")}</Label>
              <Textarea
                id="message"
                placeholder={t("contact.message_placeholder")}
                rows={5}
                required
              />
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90">
              {t("contact.send_message")}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Contact;
