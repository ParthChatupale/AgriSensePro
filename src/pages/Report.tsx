import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MapPin, Upload, Wifi, WifiOff } from "lucide-react";
import { toast } from "sonner";
import { submitReport } from "../services/api";
import { useTranslation } from "react-i18next";


const Report = () => {
  const { t } = useTranslation();
  const [isOnline] = useState(true);
  const [formData, setFormData] = useState({
    crop: "",
    issueType: "",
    severity: "",
    notes: "",
    location: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isOnline) {
      toast.success(t("report.success"));
    } else {
      toast.info(t("report.saved_offline"));
    }
  };

  const detectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
          setFormData({ ...formData, location: coords });
          toast.success(t("report.location_detected"));
        },
        () => {
          toast.error(t("report.location_error"));
        }
      );
    }
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-heading font-bold text-primary">{t("report.title")}</h1>
            <div className="flex items-center gap-2 text-sm">
              {isOnline ? (
                <span className="flex items-center gap-1 text-success">
                  <Wifi className="h-4 w-4" />
                  {t("report.online")}
                </span>
              ) : (
                <span className="flex items-center gap-1 text-warning">
                  <WifiOff className="h-4 w-4" />
                  {t("report.offline")}
                </span>
              )}
            </div>
          </div>
          <p className="text-muted-foreground">
            {t("report.subtitle")}
          </p>
        </div>

        <Card className="p-6 shadow-hover bg-gradient-card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="crop">{t("report.crop_type")} *</Label>
              <Select
                value={formData.crop}
                onValueChange={(value) => setFormData({ ...formData, crop: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder={t("report.select_crop")} />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="wheat">{t("advisory.crops.wheat")}</SelectItem>
                  <SelectItem value="rice">{t("advisory.crops.rice")}</SelectItem>
                  <SelectItem value="cotton">{t("advisory.crops.cotton")}</SelectItem>
                  <SelectItem value="sugarcane">{t("advisory.crops.sugarcane")}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="issueType">{t("report.issue_type")} *</Label>
              <Select
                value={formData.issueType}
                onValueChange={(value) => setFormData({ ...formData, issueType: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder={t("report.select_issue_type")} />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="pest">{t("report.issue.pest")}</SelectItem>
                  <SelectItem value="disease">{t("report.issue.disease")}</SelectItem>
                  <SelectItem value="weather">{t("report.issue.weather")}</SelectItem>
                  <SelectItem value="other">{t("report.issue.other")}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="severity">{t("report.severity")} *</Label>
              <Select
                value={formData.severity}
                onValueChange={(value) => setFormData({ ...formData, severity: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder={t("report.select_severity")} />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="low">{t("report.severity_level.low")}</SelectItem>
                  <SelectItem value="medium">{t("report.severity_level.medium")}</SelectItem>
                  <SelectItem value="high">{t("report.severity_level.high")}</SelectItem>
                  <SelectItem value="critical">{t("report.severity_level.critical")}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">{t("report.gps_coordinates")}</Label>
              <div className="flex gap-2">
                <Input
                  id="location"
                  type="text"
                  placeholder={t("report.gps_placeholder")}
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  readOnly
                />
                <Button type="button" variant="outline" onClick={detectLocation}>
                  <MapPin className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">{t("report.additional_notes")}</Label>
              <Textarea
                id="notes"
                placeholder={t("report.notes_placeholder")}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="photo">{t("report.upload_photo")}</Label>
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {t("report.upload_hint")}
                </p>
                <input type="file" id="photo" accept="image/*" className="hidden" />
              </div>
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90">
              {t("report.submit")}
            </Button>
          </form>
        </Card>

        {/* Offline Queue (shown when offline) */}
        {!isOnline && (
          <Card className="mt-6 p-4 bg-warning/10 border-warning/20">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <WifiOff className="h-4 w-4" />
              {t("report.offline_queue")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("report.offline_queue_desc")}
            </p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Report;
