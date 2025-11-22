import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Heart, MessageCircle, Loader2, ArrowLeft, Send } from "lucide-react";
import { useTranslation } from "react-i18next";
import { getUserPosts, togglePostLike, getPostComments, createComment, type Post, type Comment } from "@/services/api";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { isAuthenticated } from "@/services/api";

const UserProfile = () => {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [likingPostId, setLikingPostId] = useState<number | null>(null);
  const [openCommentsPostId, setOpenCommentsPostId] = useState<number | null>(null);
  const [comments, setComments] = useState<Record<number, Comment[]>>({});
  const [loadingComments, setLoadingComments] = useState<Record<number, boolean>>({});
  const [newComment, setNewComment] = useState<Record<number, string>>({});
  const [postingComment, setPostingComment] = useState<number | null>(null);
  const [userName, setUserName] = useState<string>("");

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    if (!userId) {
      navigate("/community");
      return;
    }

    const fetchUserPosts = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const postsData = await getUserPosts(parseInt(userId));
        setPosts(postsData);
        if (postsData.length > 0) {
          setUserName(postsData[0].author_name || postsData[0].author?.name || "User");
        }
      } catch (err: any) {
        setError(err.message || "Failed to load user posts");
        toast.error(err.message || "Failed to load user posts");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserPosts();
  }, [userId, navigate]);

  const handleLike = async (postId: number) => {
    if (likingPostId) return;
    
    setLikingPostId(postId);
    try {
      const result = await togglePostLike(postId);
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, likes_count: result.likes_count, is_liked: result.is_liked }
          : post
      ));
    } catch (err: any) {
      toast.error(err.message || "Failed to like post");
    } finally {
      setLikingPostId(null);
    }
  };

  const handleCommentClick = async (postId: number) => {
    if (openCommentsPostId === postId) {
      setOpenCommentsPostId(null);
      return;
    }

    setOpenCommentsPostId(postId);
    setLoadingComments(prev => ({ ...prev, [postId]: true }));
    
    try {
      const commentsData = await getPostComments(postId);
      setComments(prev => ({ ...prev, [postId]: commentsData }));
    } catch (err: any) {
      toast.error(err.message || "Failed to load comments");
      setOpenCommentsPostId(null);
    } finally {
      setLoadingComments(prev => ({ ...prev, [postId]: false }));
    }
  };

  const handleSubmitComment = async (postId: number) => {
    const commentText = newComment[postId]?.trim();
    if (!commentText) {
      toast.error(t("community.comment_required"));
      return;
    }

    setPostingComment(postId);
    try {
      const newCommentData = await createComment(postId, { content: commentText });
      
      setComments(prev => ({
        ...prev,
        [postId]: [...(prev[postId] || []), newCommentData]
      }));
      
      setPosts(prev => prev.map(post => 
        post.id === postId 
          ? { ...post, comments_count: post.comments_count + 1 }
          : post
      ));
      
      setNewComment(prev => ({ ...prev, [postId]: "" }));
      toast.success(t("community.comment_posted"));
    } catch (err: any) {
      toast.error(err.message || "Failed to post comment");
    } finally {
      setPostingComment(null);
    }
  };

  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t("community.just_now");
    if (diffMins < 60) return t("community.minutes_ago", { count: diffMins });
    if (diffHours < 24) return t("community.hours_ago", { count: diffHours });
    if (diffDays < 7) return t("community.days_ago", { count: diffDays });
    
    return date.toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const LoadingSkeleton = () => (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="p-6">
          <div className="flex items-start gap-4">
            <Skeleton className="w-12 h-12 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-24" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate("/community")}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t("community.back_to_community") || "Back to Community"}
        </Button>

        <div className="mb-6">
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">
            {userName ? `${userName}'s Posts` : "User Posts"}
          </h1>
          <p className="text-muted-foreground">
            {posts.length} {posts.length === 1 ? "post" : "posts"}
          </p>
        </div>

        {isLoading ? (
          <LoadingSkeleton />
        ) : error ? (
          <Card className="p-6 text-center">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => window.location.reload()} variant="outline">
              {t("community.retry")}
            </Button>
          </Card>
        ) : posts.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground mb-4">{t("community.no_posts")}</p>
          </Card>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <Card key={post.id} className="p-6 hover:shadow-hover transition-all bg-gradient-card">
                <div className="flex items-start gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {(post.author_name || post.author?.name || "U").charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h3 className="font-semibold">{post.author_name || post.author?.name || "Unknown"}</h3>
                      <span className="text-sm text-muted-foreground">• {post.region || "Unknown"}</span>
                      {post.crop && (
                        <Badge variant="outline" className="text-xs">
                          {post.crop}
                        </Badge>
                      )}
                      {post.category && (
                        <Badge variant="secondary" className="text-xs">
                          {t(`community.category.${post.category}`) || post.category}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">• {formatTimestamp(post.created_at)}</span>
                    </div>
                    <p className="text-foreground mb-4 whitespace-pre-wrap">{post.content}</p>

                    {post.image_url && (
                      <div className="mb-4 rounded-lg overflow-hidden border">
                        <img 
                          src={post.image_url} 
                          alt="Post image" 
                          className="w-full h-auto max-h-96 object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <button 
                        onClick={() => handleLike(post.id)}
                        disabled={likingPostId === post.id}
                        className={`flex items-center gap-2 transition-colors ${
                          post.is_liked 
                            ? "text-destructive" 
                            : "hover:text-destructive"
                        } ${likingPostId === post.id ? "opacity-50 cursor-not-allowed" : ""}`}
                      >
                        {likingPostId === post.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Heart className={`h-4 w-4 ${post.is_liked ? "fill-current" : ""}`} />
                        )}
                        <span>{post.likes_count}</span>
                      </button>
                      <button 
                        onClick={() => handleCommentClick(post.id)}
                        className={`flex items-center gap-2 transition-colors ${
                          openCommentsPostId === post.id 
                            ? "text-primary" 
                            : "hover:text-primary"
                        }`}
                      >
                        <MessageCircle className="h-4 w-4" />
                        <span>{post.comments_count}</span>
                      </button>
                    </div>

                    {openCommentsPostId === post.id && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="space-y-3">
                          {loadingComments[post.id] ? (
                            <div className="space-y-2">
                              <Skeleton className="h-16 w-full" />
                              <Skeleton className="h-16 w-full" />
                            </div>
                          ) : (
                            <>
                              {comments[post.id] && comments[post.id].length > 0 ? (
                                <div className="space-y-3 max-h-64 overflow-y-auto">
                                  {comments[post.id].map((comment) => (
                                    <div key={comment.id} className="flex gap-3">
                                      <Avatar className="w-8 h-8">
                                        <AvatarFallback className="bg-muted text-foreground text-xs">
                                          {(comment.author_name || "U").charAt(0).toUpperCase()}
                                        </AvatarFallback>
                                      </Avatar>
                                      <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                          <span className="font-medium text-sm">{comment.author_name || "Unknown"}</span>
                                          <span className="text-xs text-muted-foreground">
                                            {formatTimestamp(comment.created_at)}
                                          </span>
                                        </div>
                                        <p className="text-sm text-foreground whitespace-pre-wrap">{comment.content}</p>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-sm text-muted-foreground text-center py-2">
                                  {t("community.no_comments")}
                                </p>
                              )}

                              <div className="flex gap-2 pt-2">
                                <Input
                                  placeholder={t("community.write_comment")}
                                  value={newComment[post.id] || ""}
                                  onChange={(e) => setNewComment(prev => ({ ...prev, [post.id]: e.target.value }))}
                                  onKeyDown={(e) => {
                                    if (e.key === "Enter" && !e.shiftKey) {
                                      e.preventDefault();
                                      handleSubmitComment(post.id);
                                    }
                                  }}
                                  disabled={postingComment === post.id}
                                  className="flex-1"
                                />
                                <Button
                                  size="sm"
                                  onClick={() => handleSubmitComment(post.id)}
                                  disabled={postingComment === post.id || !newComment[post.id]?.trim()}
                                >
                                  {postingComment === post.id ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                  ) : (
                                    <Send className="h-4 w-4" />
                                  )}
                                </Button>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;

