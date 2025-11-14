import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Heart, MessageCircle, Share2, Plus, TrendingUp } from "lucide-react";
import { useTranslation } from "react-i18next";

const Community = () => {
  const { t } = useTranslation();
  const [posts] = useState([
    {
      id: 1,
      author: "Rajesh Kumar",
      region: "Punjab",
      content: "Just harvested my wheat crop! Yield is 20% better than last year thanks to the advisory tips from AgriSense. 🌾",
      likes: 45,
      comments: 12,
      verified: true,
      image: null,
    },
    {
      id: 2,
      author: "Priya Sharma",
      region: "Maharashtra",
      content: "Has anyone tried the neem-based pesticide for cotton? Looking for recommendations.",
      likes: 23,
      comments: 8,
      verified: false,
      image: null,
    },
    {
      id: 3,
      author: "Anil Patel",
      region: "Gujarat",
      content: "Great weather forecast accuracy! Helped me plan irrigation perfectly this week.",
      likes: 67,
      comments: 15,
      verified: true,
      image: null,
    },
  ]);

  const topContributors = [
    { name: "Rajesh K.", posts: 24 },
    { name: "Priya S.", posts: 18 },
    { name: "Anil P.", posts: 15 },
  ];

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Feed */}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-heading font-bold text-primary mb-2">{t("community.title")}</h1>
                <p className="text-muted-foreground">{t("community.subtitle")}</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90 gap-2">
                <Plus className="h-4 w-4" />
                {t("community.post_update")}
              </Button>
            </div>

            <div className="space-y-4">
              {posts.map((post) => (
                <Card key={post.id} className="p-6 hover:shadow-hover transition-all bg-gradient-card">
                  <div className="flex items-start gap-4">
                    <Avatar className="w-12 h-12">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {post.author.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">{post.author}</h3>
                        {post.verified && (
                          <Badge variant="default" className="text-xs bg-success">
                            ✓ {t("community.verified")}
                          </Badge>
                        )}
                        <span className="text-sm text-muted-foreground">• {post.region}</span>
                      </div>
                      <p className="text-foreground mb-4">{post.content}</p>

                      {/* Actions */}
                      <div className="flex items-center gap-6 text-sm text-muted-foreground">
                        <button className="flex items-center gap-2 hover:text-destructive transition-colors">
                          <Heart className="h-4 w-4" />
                          <span>{post.likes}</span>
                        </button>
                        <button className="flex items-center gap-2 hover:text-primary transition-colors">
                          <MessageCircle className="h-4 w-4" />
                          <span>{post.comments}</span>
                        </button>
                        <button className="flex items-center gap-2 hover:text-secondary transition-colors">
                          <Share2 className="h-4 w-4" />
                          <span>{t("community.share")}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:w-80 space-y-6">
            {/* Top Contributors */}
            <Card className="p-6 bg-gradient-card">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <h3 className="font-heading font-bold">{t("community.top_contributors")}</h3>
              </div>
              <div className="space-y-3">
                {topContributors.map((contributor, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-lg text-muted-foreground">#{idx + 1}</span>
                      <Avatar className="w-8 h-8">
                        <AvatarFallback className="bg-muted text-foreground">
                          {contributor.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{contributor.name}</span>
                    </div>
                    <Badge variant="secondary">{t("community.posts_count", { count: contributor.posts })}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            {/* Trending Topics */}
            <Card className="p-6 bg-gradient-card">
              <h3 className="font-heading font-bold mb-4">{t("community.trending_topics")}</h3>
              <div className="space-y-2">
                {["#OrganicFarming", "#PestControl", "#IrrigationTips", "#WeatherUpdate"].map((tag) => (
                  <button
                    key={tag}
                    className="block w-full text-left px-3 py-2 rounded-md bg-muted hover:bg-muted/70 transition-colors text-sm font-medium text-primary"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Community;
