import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Heart, MessageCircle, Share2, Plus, TrendingUp, Loader2, Send, Search, Edit, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { getCommunityPosts, togglePostLike, createPost, getPostComments, createComment, getTopContributors, uploadImage, searchPosts, updatePost, deletePost, getTrendingTopics, getCurrentUser, type Post, type CreatePostData, type Comment, type TopContributor, type TrendingTopic } from "@/services/api";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const Community = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [likingPostId, setLikingPostId] = useState<number | null>(null);
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [postContent, setPostContent] = useState("");
  const [postImageFile, setPostImageFile] = useState<File | null>(null);
  const [postCrop, setPostCrop] = useState<string>("none");
  const [postCategory, setPostCategory] = useState<string>("none");
  const [isCreatingPost, setIsCreatingPost] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCrop, setSelectedCrop] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [openCommentsPostId, setOpenCommentsPostId] = useState<number | null>(null);
  const [comments, setComments] = useState<Record<number, Comment[]>>({});
  const [loadingComments, setLoadingComments] = useState<Record<number, boolean>>({});
  const [newComment, setNewComment] = useState<Record<number, string>>({});
  const [postingComment, setPostingComment] = useState<number | null>(null);
  const [topContributors, setTopContributors] = useState<TopContributor[]>([]);
  const [loadingContributors, setLoadingContributors] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [isEditingPost, setIsEditingPost] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([]);
  const [loadingTrending, setLoadingTrending] = useState(true);

  // Get current user ID on mount
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const user = await getCurrentUser();
        if (user.id) {
          setCurrentUserId(user.id);
        }
      } catch (err) {
        // User not logged in or error - ignore
      }
    };
    fetchCurrentUser();
  }, []);

  // Fetch posts, top contributors, and trending topics on component mount and when filters change
  useEffect(() => {
    if (searchQuery.trim()) return; // Don't fetch if searching
    
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const filters: { crop?: string; category?: string } = {};
        if (selectedCrop && selectedCrop !== "all") filters.crop = selectedCrop;
        if (selectedCategory && selectedCategory !== "all") filters.category = selectedCategory;
        
        const [postsData, contributorsData, trendingData] = await Promise.all([
          getCommunityPosts(Object.keys(filters).length > 0 ? filters : undefined),
          getTopContributors(10),
          getTrendingTopics(10).catch(() => []) // Fallback to empty array if error
        ]);
        setPosts(postsData);
        setTopContributors(contributorsData);
        setTrendingTopics(trendingData);
      } catch (err: any) {
        setError(err.message || "Failed to load posts");
        toast.error(err.message || "Failed to load community posts");
      } finally {
        setIsLoading(false);
        setLoadingContributors(false);
        setLoadingTrending(false);
      }
    };
    fetchData();
  }, [selectedCrop, selectedCategory]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (searchQuery.trim()) {
        setIsLoading(true);
        setError(null);
        try {
          const postsData = await searchPosts(searchQuery);
          setPosts(postsData);
        } catch (err: any) {
          setError(err.message || "Failed to search posts");
          toast.error(err.message || "Failed to search posts");
        } finally {
          setIsLoading(false);
        }
      } else if (selectedCrop === "all" && selectedCategory === "all") {
        // Only reload if no filters are active
        const fetchData = async () => {
          setIsLoading(true);
          setError(null);
          try {
            const postsData = await getCommunityPosts();
            setPosts(postsData);
          } catch (err: any) {
            setError(err.message || "Failed to load posts");
            toast.error(err.message || "Failed to load community posts");
          } finally {
            setIsLoading(false);
          }
        };
        fetchData();
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Handle image file selection
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Invalid file type. Please select an image file.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image is too large. Maximum size is 5MB.");
      return;
    }

    setPostImageFile(file);
  };

  // Handle post creation
  const handleCreatePost = async () => {
    if (!postContent.trim()) {
      toast.error(t("community.post_content_required"));
      return;
    }

    setIsCreatingPost(true);
    let imageUrl: string | undefined = undefined;

    // Upload image if selected
    if (postImageFile) {
      setIsUploadingImage(true);
      try {
        imageUrl = await uploadImage(postImageFile);
      } catch (err: any) {
        setIsUploadingImage(false);
        setIsCreatingPost(false);
        toast.error(err.message || "Failed to upload image");
        return;
      }
      setIsUploadingImage(false);
    }

    try {
      const postData: CreatePostData = {
        content: postContent.trim(),
        crop: postCrop && postCrop !== "none" ? postCrop : undefined,
        category: postCategory && postCategory !== "none" ? postCategory : undefined,
        image_url: imageUrl,
      };
      const newPost = await createPost(postData);
      
      // Refresh posts and contributors
      const filters: { crop?: string; category?: string } = {};
      if (selectedCrop && selectedCrop !== "all") filters.crop = selectedCrop;
      if (selectedCategory && selectedCategory !== "all") filters.category = selectedCategory;
      
      const [postsData, contributorsData] = await Promise.all([
        getCommunityPosts(Object.keys(filters).length > 0 ? filters : undefined),
        getTopContributors(10)
      ]);
      setPosts(postsData);
      setTopContributors(contributorsData);
      
      // Reset form and close modal
      setPostContent("");
      setPostImageFile(null);
      setPostCrop("none");
      setPostCategory("none");
      setIsPostModalOpen(false);
      toast.success(t("community.post_created_success"));
    } catch (err: any) {
      toast.error(err.message || t("community.post_create_error"));
    } finally {
      setIsCreatingPost(false);
    }
  };

  // Handle comment button click
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

  // Handle comment submission
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

  // Handle like toggle
  const handleLike = async (postId: number) => {
    if (likingPostId) return; // Prevent multiple simultaneous likes
    
    setLikingPostId(postId);
    try {
      const result = await togglePostLike(postId);
      // Update the post in the list
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

  // Handle edit post
  const handleEditPost = (post: Post) => {
    setEditingPostId(post.id);
    setPostContent(post.content);
    setPostCrop(post.crop || "none");
    setPostCategory(post.category || "none");
    setPostImageFile(null);
    setIsEditingPost(true);
    setIsPostModalOpen(true);
  };

  // Handle delete post
  const handleDeletePost = async (postId: number) => {
    if (!confirm(t("community.confirm_delete") || "Are you sure you want to delete this post?")) {
      return;
    }

    try {
      await deletePost(postId);
      setPosts(posts.filter(post => post.id !== postId));
      toast.success(t("community.post_deleted") || "Post deleted successfully");
    } catch (err: any) {
      toast.error(err.message || "Failed to delete post");
    }
  };

  // Handle update post
  const handleUpdatePost = async () => {
    if (!postContent.trim() || !editingPostId) {
      toast.error(t("community.post_content_required"));
      return;
    }

    setIsCreatingPost(true);
    let imageUrl: string | undefined = undefined;

    // Upload image if selected
    if (postImageFile) {
      setIsUploadingImage(true);
      try {
        imageUrl = await uploadImage(postImageFile);
      } catch (err: any) {
        setIsUploadingImage(false);
        setIsCreatingPost(false);
        toast.error(err.message || "Failed to upload image");
        return;
      }
      setIsUploadingImage(false);
    }

    try {
      const updateData: { content: string; crop?: string; category?: string; image_url?: string } = {
        content: postContent.trim(),
        crop: postCrop && postCrop !== "none" ? postCrop : undefined,
        category: postCategory && postCategory !== "none" ? postCategory : undefined,
      };
      if (imageUrl) {
        updateData.image_url = imageUrl;
      }

      const updatedPost = await updatePost(editingPostId, updateData);
      
      // Update the post in the list
      setPosts(posts.map(post => 
        post.id === editingPostId ? updatedPost : post
      ));
      
      // Reset form and close modal
      setPostContent("");
      setPostImageFile(null);
      setPostCrop("none");
      setPostCategory("none");
      setEditingPostId(null);
      setIsEditingPost(false);
      setIsPostModalOpen(false);
      toast.success(t("community.post_updated") || "Post updated successfully");
    } catch (err: any) {
      toast.error(err.message || t("community.post_update_error") || "Failed to update post");
    } finally {
      setIsCreatingPost(false);
    }
  };

  // Format timestamp
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


  // Loading skeleton
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
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Feed */}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-heading font-bold text-primary mb-2">{t("community.title")}</h1>
                <p className="text-muted-foreground">{t("community.subtitle")}</p>
              </div>
              <Button 
                className="bg-primary hover:bg-primary/90 gap-2"
                onClick={() => setIsPostModalOpen(true)}
              >
                <Plus className="h-4 w-4" />
                {t("community.post_update")}
              </Button>
            </div>

            {/* Search Input */}
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder={t("community.search_placeholder")}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
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
                          <h3 
                            className="font-semibold cursor-pointer hover:text-primary transition-colors"
                            onClick={() => navigate(`/profile/${post.author_id}`)}
                          >
                            {post.author_name || post.author?.name || "Unknown"}
                          </h3>
                          <span className="text-sm text-muted-foreground">• {post.region || "Unknown"}</span>
                          {currentUserId === post.author_id && (
                            <div className="flex items-center gap-2 ml-auto">
                              <button
                                onClick={() => handleEditPost(post)}
                                className="text-muted-foreground hover:text-primary transition-colors"
                                title={t("community.edit_post") || "Edit post"}
                              >
                                <Edit className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDeletePost(post.id)}
                                className="text-muted-foreground hover:text-destructive transition-colors"
                                title={t("community.delete_post") || "Delete post"}
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          )}
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

                        {/* Post Image */}
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

                        {/* Actions */}
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
                          <button className="flex items-center gap-2 hover:text-secondary transition-colors">
                            <Share2 className="h-4 w-4" />
                            <span>{t("community.share")}</span>
                          </button>
                        </div>

                        {/* Comments Section */}
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

          {/* Sidebar */}
          <div className="lg:w-80 space-y-6">
            {/* Top Contributors */}
            <Card className="p-6 bg-gradient-card">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <h3 className="font-heading font-bold">{t("community.top_contributors")}</h3>
              </div>
              {loadingContributors ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Skeleton className="w-6 h-6" />
                        <Skeleton className="w-8 h-8 rounded-full" />
                        <Skeleton className="h-4 w-24" />
                      </div>
                      <Skeleton className="h-5 w-16" />
                    </div>
                  ))}
                </div>
              ) : topContributors.length > 0 ? (
                <div className="space-y-3">
                  {topContributors.map((contributor, idx) => (
                    <div key={contributor.user_id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-lg text-muted-foreground">#{idx + 1}</span>
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="bg-muted text-foreground">
                            {contributor.name.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <span className="font-medium">{contributor.name}</span>
                      </div>
                      <Badge variant="secondary">{t("community.posts_count", { count: contributor.posts_count })}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  {t("community.no_contributors")}
                </p>
              )}
            </Card>

            {/* Filters */}
            <Card className="p-6 bg-gradient-card">
              <h3 className="font-heading font-bold mb-4">{t("community.filter_by_crop")}</h3>
              <Select value={selectedCrop} onValueChange={setSelectedCrop}>
                <SelectTrigger>
                  <SelectValue placeholder={t("community.select_crop")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("community.all_crops")}</SelectItem>
                  <SelectItem value="rice">Rice</SelectItem>
                  <SelectItem value="wheat">Wheat</SelectItem>
                  <SelectItem value="cotton">Cotton</SelectItem>
                  <SelectItem value="sugarcane">Sugarcane</SelectItem>
                  <SelectItem value="soybean">Soybean</SelectItem>
                  <SelectItem value="onion">Onion</SelectItem>
                </SelectContent>
              </Select>
              <h3 className="font-heading font-bold mb-4 mt-4">{t("community.filter_by_category")}</h3>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder={t("community.select_category")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("community.all_categories")}</SelectItem>
                  <SelectItem value="tip">{t("community.tip")}</SelectItem>
                  <SelectItem value="question">{t("community.question")}</SelectItem>
                  <SelectItem value="issue">{t("community.issue")}</SelectItem>
                  <SelectItem value="success">{t("community.success")}</SelectItem>
                </SelectContent>
              </Select>
            </Card>

            {/* Trending Topics */}
            <Card className="p-6 bg-gradient-card">
              <h3 className="font-heading font-bold mb-4">{t("community.trending_topics")}</h3>
              {loadingTrending ? (
                <div className="space-y-2">
                  {[1, 2, 3, 4].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : trendingTopics.length > 0 ? (
                <div className="space-y-2">
                  {trendingTopics.map((topic) => (
                    <button
                      key={topic.tag}
                      className="block w-full text-left px-3 py-2 rounded-md bg-muted hover:bg-muted/70 transition-colors text-sm font-medium text-primary"
                      onClick={() => {
                        setSearchQuery(`#${topic.tag}`);
                      }}
                    >
                      #{topic.tag} ({topic.count})
                    </button>
                  ))}
                </div>
              ) : (
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
              )}
            </Card>
          </div>
        </div>
      </div>

      {/* Post Creation Modal */}
      <Dialog open={isPostModalOpen} onOpenChange={setIsPostModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{isEditingPost ? (t("community.edit_post") || "Edit Post") : t("community.create_post")}</DialogTitle>
            <DialogDescription>
              {isEditingPost ? (t("community.edit_post_description") || "Update your post") : t("community.create_post_description")}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Textarea
              placeholder={t("community.post_placeholder")}
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              className="min-h-[150px] resize-none"
              disabled={isCreatingPost}
            />
            <Input
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              disabled={isCreatingPost || isUploadingImage}
              className="cursor-pointer"
            />
            <Select value={postCrop} onValueChange={setPostCrop}>
              <SelectTrigger>
                <SelectValue placeholder={t("community.select_crop")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{t("community.select_crop")}</SelectItem>
                <SelectItem value="rice">Rice</SelectItem>
                <SelectItem value="wheat">Wheat</SelectItem>
                <SelectItem value="cotton">Cotton</SelectItem>
                <SelectItem value="sugarcane">Sugarcane</SelectItem>
                <SelectItem value="soybean">Soybean</SelectItem>
                <SelectItem value="onion">Onion</SelectItem>
              </SelectContent>
            </Select>
            <Select value={postCategory} onValueChange={setPostCategory}>
              <SelectTrigger>
                <SelectValue placeholder={t("community.select_category")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{t("community.select_category")}</SelectItem>
                <SelectItem value="tip">{t("community.tip")}</SelectItem>
                <SelectItem value="question">{t("community.question")}</SelectItem>
                <SelectItem value="issue">{t("community.issue")}</SelectItem>
                <SelectItem value="success">{t("community.success")}</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {t("community.post_hint")}
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsPostModalOpen(false);
                setPostContent("");
                setPostImageFile(null);
                setPostCrop("none");
                setPostCategory("none");
                setEditingPostId(null);
                setIsEditingPost(false);
              }}
              disabled={isCreatingPost}
            >
              {t("community.cancel")}
            </Button>
            <Button
              onClick={isEditingPost ? handleUpdatePost : handleCreatePost}
              disabled={isCreatingPost || isUploadingImage || !postContent.trim()}
              className="bg-primary hover:bg-primary/90"
            >
              {isCreatingPost || isUploadingImage ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {isUploadingImage ? t("community.uploading_image") : t("community.posting")}
                </>
              ) : (
                isEditingPost ? (t("community.update") || "Update") : t("community.post")
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Community;
