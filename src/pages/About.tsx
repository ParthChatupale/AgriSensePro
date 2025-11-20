import { Card } from "@/components/ui/card";
import { Target, Users, Lightbulb } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-heading font-bold text-primary mb-4">About krushiRakshak</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Transforming Indian agriculture through technology and community
          </p>
        </div>

        <div className="space-y-8 mb-12">
          <Card className="p-8 shadow-hover bg-gradient-card">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Target className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-heading font-bold mb-4">Our Mission</h2>
                <p className="text-muted-foreground leading-relaxed">
                  krushiRakshak is dedicated to empowering farmers with intelligent, data-driven insights that
                  help them make better decisions. We combine satellite technology, weather data, and
                  community knowledge to create a comprehensive farming assistant that's accessible to all.
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-8 shadow-hover bg-gradient-card">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center flex-shrink-0">
                <Users className="h-6 w-6 text-secondary" />
              </div>
              <div>
                <h2 className="text-2xl font-heading font-bold mb-4">Our Community</h2>
                <p className="text-muted-foreground leading-relaxed">
                  We believe in the power of community. krushiRakshak brings farmers together to share
                  knowledge, experiences, and solutions. By connecting farmers across regions, we're
                  building a network of support that helps everyone grow stronger together.
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-8 shadow-hover bg-gradient-card">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                <Lightbulb className="h-6 w-6 text-accent" />
              </div>
              <div>
                <h2 className="text-2xl font-heading font-bold mb-4">Innovation for All</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Built with the latest technology but designed for simplicity, krushiRakshak works offline,
                  supports multiple languages, and provides actionable insights in an easy-to-understand
                  format. We're making advanced farming technology accessible to every farmer, regardless
                  of their technical expertise.
                </p>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-8 bg-gradient-hero text-white text-center">
          <h2 className="text-2xl font-heading font-bold mb-4">Join Our Journey</h2>
          <p className="text-lg opacity-90 mb-6">
            krushiRakshak is constantly evolving, and we're committed to adding more features that serve
            the farming community better. Your feedback helps us grow.
          </p>
          <p className="text-sm opacity-75">
            This project was developed as part of an innovation initiative to support Indian farmers.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default About;
