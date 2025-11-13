import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Download, CheckCircle, Droplets, Sprout, Eye, Loader2, AlertTriangle, ArrowLeft } from "lucide-react";
import { getAdvisory, getCurrentUser } from "@/services/api";
import type { AdvisoryResponse, Recommendation } from "@/types/fusion";

const AVAILABLE_CROPS = [
  { value: "cotton", label: "Cotton" },
  { value: "wheat", label: "Wheat" },
  { value: "rice", label: "Rice" },
  { value: "sugarcane", label: "Sugarcane" },
  { value: "soybean", label: "Soybean" },
  { value: "onion", label: "Onion" },
];

const Advisory = () => {
  const { crop: cropParam } = useParams<{ crop: string }>();
  const navigate = useNavigate();
  const [selectedCrop, setSelectedCrop] = useState<string>(cropParam || "cotton");
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load user's crop on mount if no crop param
  useEffect(() => {
    const loadUserCrop = async () => {
      if (!cropParam) {
        try {
          const user = await getCurrentUser();
          if (user.crop) {
            setSelectedCrop(user.crop);
          }
        } catch (err) {
          // Silently fail - default to cotton
        }
      }
    };
    loadUserCrop();
  }, [cropParam]);

  useEffect(() => {
    // Update selected crop from URL param if it changes
    if (cropParam && cropParam !== selectedCrop) {
      setSelectedCrop(cropParam);
    }
  }, [cropParam]);

  useEffect(() => {
    if (!selectedCrop) {
      setError("No crop specified. Please select a crop.");
      setIsLoading(false);
      return;
    }

    const fetchAdvisory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getAdvisory(selectedCrop);
        setAdvisory(data);
        // Update URL without navigation
        navigate(`/advisory/${selectedCrop}`, { replace: true });
      } catch (err: any) {
        setError(err.message || "Unable to load advisory data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAdvisory();
  }, [selectedCrop, navigate]);

  const getPriorityVariant = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "default";
    }
  };

  const getRecommendationIcon = (title: string) => {
    const lowerTitle = title.toLowerCase();
    if (lowerTitle.includes("irrigat") || lowerTitle.includes("water") || lowerTitle.includes("moisture")) {
      return Droplets;
    }
    if (lowerTitle.includes("monitor") || lowerTitle.includes("check") || lowerTitle.includes("inspect")) {
      return Eye;
    }
    return Sprout;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Recently";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-IN", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "Recently";
    }
  };

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Skeleton className="h-10 w-32 mb-4" />
          <Skeleton className="h-9 w-64 mb-2" />
          <Skeleton className="h-5 w-96" />
        </div>
        <Card className="p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4 mb-6" />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-muted/50">
                <Skeleton className="h-5 w-48 mb-2" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );

  // Loading state
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  // Minimal guard to avoid crashes if advisory missing
  if (!advisory) return <div className="p-10 text-center text-lg">Loading advisory...</div>;

  // Safe fallbacks for scores
  const pestScore = advisory?.rule_breakdown?.pest?.score || 0;
  const irrigationScore = advisory?.rule_breakdown?.irrigation?.score || 0;
  const marketScore = advisory?.rule_breakdown?.market?.score || 0;
  const pestFired = advisory?.rule_breakdown?.pest?.fired?.length || 0;
  const irrigationFired = advisory?.rule_breakdown?.irrigation?.fired?.length || 0;
  const marketFired = advisory?.rule_breakdown?.market?.fired?.length || 0;

  // Error state (kept for other errors)
  if (error) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-destructive" />
          <h2 className="text-2xl font-bold mb-2">Unable to Load Advisory</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <div className="flex gap-2 justify-center">
            <Button onClick={() => navigate("/dashboard")} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/dashboard")}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div>
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">Advisory Details</h1>
          <p className="text-muted-foreground">Personalized recommendations based on your farm data</p>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="crop-select" className="text-sm text-muted-foreground whitespace-nowrap">
                Select Crop:
              </label>
              <Select value={selectedCrop} onValueChange={setSelectedCrop}>
                <SelectTrigger id="crop-select" className="w-[180px]">
                  <SelectValue placeholder="Select crop" />
                </SelectTrigger>
                <SelectContent>
                  {AVAILABLE_CROPS.map((crop) => (
                    <SelectItem key={crop.value} value={crop.value}>
                      {crop.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Main Advisory Card */}
        <Card className="p-6 mb-6 shadow-hover bg-gradient-card">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={getPriorityVariant(advisory.priority)} className="mb-2">
                  {advisory.priority} Priority
                </Badge>
                <Badge variant="outline" className="mb-2">
                  {advisory.severity} Severity
                </Badge>
              </div>
              <h2 className="text-2xl font-heading font-bold mb-2">
                {advisory.crop} Crop Advisory
              </h2>
              <p className="text-muted-foreground">
                Last updated: {formatDate(advisory.last_updated)}
                {advisory.rule_score > 0 && ` • Confidence: ${Math.round(advisory.rule_score * 100)}%`}
              </p>
            </div>
          </div>

          <div className="prose prose-sm max-w-none mb-6">
            <h3 className="font-semibold text-lg mb-2">Analysis</h3>
            <p className="text-muted-foreground mb-4">{advisory.analysis}</p>

            {/* Fired Rules */}
            {advisory.fired_rules && advisory.fired_rules.length > 0 && (
              <div className="mb-4">
                <h3 className="font-semibold text-lg mb-2">Triggered Rules</h3>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                  {advisory.fired_rules.map((rule, idx) => (
                    <li key={idx} className="text-sm">{rule}</li>
                  ))}
                </ul>
              </div>
            )}

            <h3 className="font-semibold text-lg mb-2">Recommended Actions</h3>
          </div>

          <div className="space-y-4 mb-6">
            {advisory.recommendations && advisory.recommendations.length > 0 ? (
              advisory.recommendations.map((rec: Recommendation, idx: number) => {
                const Icon = getRecommendationIcon(rec.title);
                return (
              <div
                key={idx}
                className="flex items-start gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold">{rec.title}</h4>
                    <Badge
                          variant={getPriorityVariant(rec.priority)}
                      className="text-xs"
                    >
                      {rec.priority}
                    </Badge>
                  </div>
                      <p className="text-sm text-muted-foreground">{rec.desc}</p>
                      {rec.timeline && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Timeline: {rec.timeline}
                        </p>
                      )}
                </div>
                <Button size="sm" variant="ghost">
                  <CheckCircle className="h-4 w-4" />
                </Button>
              </div>
                );
              })
            ) : (
              <p className="text-sm text-muted-foreground">No specific recommendations at this time.</p>
            )}
          </div>

          {/* Rule Breakdown */}
          {advisory?.rule_breakdown && (
            <div className="mb-6 p-4 bg-muted/30 rounded-lg">
              <h3 className="font-semibold text-sm mb-3">Rule Breakdown</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground mb-1">Pest Detection</p>
                  <p className="font-medium">Score: {Math.round(pestScore * 100)}%</p>
                  {pestFired > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">{pestFired} rule(s) triggered</p>
                  )}
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Irrigation</p>
                  <p className="font-medium">Score: {Math.round(irrigationScore * 100)}%</p>
                  {irrigationFired > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">{irrigationFired} rule(s) triggered</p>
                  )}
                </div>
                <div>
                  <p className="text-muted-foreground mb-1">Market</p>
                  <p className="font-medium">Score: {Math.round(marketScore * 100)}%</p>
                  {marketFired > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">{marketFired} rule(s) triggered</p>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <Button className="flex-1 bg-primary hover:bg-primary/90">
              <CheckCircle className="h-4 w-4 mr-2" />
              Mark as Done
            </Button>
            <Button variant="outline" className="flex-1">
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
            <Button variant="outline">Translate to मराठी</Button>
          </div>
        </Card>

        {/* Explainability Note */}
        <Card className="p-4 bg-info/10 border-info/20">
          <p className="text-sm text-foreground">
            <strong>How we determined this:</strong>{" "}
            {advisory.data_sources ? (
              <>
                This advisory is based on a combination of {advisory.data_sources.weather} weather data,{" "}
                {advisory.data_sources.satellite} satellite imagery (NDVI), and{" "}
                {advisory.data_sources.market} market prices. The rule-based engine evaluated multiple
                conditions including temperature, humidity, soil moisture, NDVI changes, and market trends
                to generate these recommendations.
              </>
            ) : (
              "This advisory is based on a combination of weather data, satellite imagery (NDVI), and market prices. The rule-based engine evaluated multiple conditions to generate these recommendations."
            )}
            {advisory.fired_rules && advisory.fired_rules.length > 0 && (
              <>
                {" "}The following rules were triggered: {advisory.fired_rules.slice(0, 2).join(", ")}
                {advisory.fired_rules.length > 2 && " and more."}
              </>
            )}
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Advisory;
