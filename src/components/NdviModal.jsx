import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, X, AlertCircle } from "lucide-react";

export function NdviModal({ isOpen, onClose, imageUrl, stats, loading, error }) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">NDVI Vegetation Map</DialogTitle>
        </DialogHeader>

        {loading && (
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="text-lg text-muted-foreground">Fetching NDVI data...</p>
            <p className="text-sm text-muted-foreground">This may take a few moments</p>
          </div>
        )}

        {error && !loading && (
          <Alert variant="destructive" className="my-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="ml-2">
              {error || "Failed to load NDVI data. Please try again."}
            </AlertDescription>
          </Alert>
        )}

        {!loading && !error && imageUrl && (
          <div className="space-y-6">
            {/* NDVI Image */}
            <div className="relative w-full rounded-lg overflow-hidden border bg-muted/50">
              <img
                src={imageUrl}
                alt="NDVI Vegetation Map"
                className="w-full h-auto object-contain"
                onError={(e) => {
                  e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Crect fill='%23f3f4f6' width='400' height='400'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%239ca3af' font-family='sans-serif' font-size='16'%3EImage not available%3C/text%3E%3C/svg%3E";
                }}
              />
            </div>

            {/* Stats Section */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg border bg-card">
                  <p className="text-sm text-muted-foreground mb-1">Min NDVI</p>
                  <p className="text-2xl font-bold">
                    {stats.min !== null && stats.min !== undefined
                      ? stats.min.toFixed(3)
                      : "—"}
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-card">
                  <p className="text-sm text-muted-foreground mb-1">Max NDVI</p>
                  <p className="text-2xl font-bold">
                    {stats.max !== null && stats.max !== undefined
                      ? stats.max.toFixed(3)
                      : "—"}
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-card">
                  <p className="text-sm text-muted-foreground mb-1">Mean NDVI</p>
                  <p className="text-2xl font-bold">
                    {stats.mean !== null && stats.mean !== undefined
                      ? stats.mean.toFixed(3)
                      : "—"}
                  </p>
                </div>
                <div className="p-4 rounded-lg border bg-card">
                  <p className="text-sm text-muted-foreground mb-1">Valid Pixels</p>
                  <p className="text-2xl font-bold">
                    {stats.valid_pixels !== null && stats.valid_pixels !== undefined
                      ? stats.valid_pixels.toLocaleString()
                      : "—"}
                  </p>
                  {stats.total_pixels && (
                    <p className="text-xs text-muted-foreground mt-1">
                      of {stats.total_pixels.toLocaleString()} total
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Info Note */}
            <div className="p-4 rounded-lg bg-muted/50 border border-muted">
              <p className="text-sm text-muted-foreground">
                <strong>NDVI Scale:</strong> Values range from -1 to +1. Higher values (green) indicate healthier vegetation.
                Values below 0.2 typically represent water, soil, or non-vegetated areas.
              </p>
            </div>
          </div>
        )}

        {!loading && !error && !imageUrl && (
          <div className="py-12 text-center">
            <p className="text-muted-foreground">No NDVI data available</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}



