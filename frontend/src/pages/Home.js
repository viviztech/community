import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Users, Calendar, Award, Heart, Target, Zap } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const HeroSection = () => {
  return (
    <section className="relative min-h-[90vh] flex items-center bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-300 rounded-full blur-3xl"></div>
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="text-center lg:text-left">
            <div className="inline-flex items-center px-4 py-2 bg-blue-700/50 rounded-full text-blue-100 text-sm mb-6">
              <Zap className="w-4 h-4 mr-2" />
              Welcome to ACTIV Community
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Building a{' '}
              <span className="text-blue-300">Stronger Community</span>{' '}
              Together
            </h1>
            <p className="text-lg text-blue-100 mb-8 max-w-xl mx-auto lg:mx-0">
              Join a vibrant community of passionate individuals dedicated to making 
              a positive impact. Together, we can achieve more.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link
                to="/register"
                className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-900 rounded-xl font-semibold text-lg hover:bg-blue-50 transition-all duration-300 hover:shadow-2xl hover:scale-105"
              >
                Become a Member
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center justify-center px-8 py-4 bg-transparent border-2 border-white/30 text-white rounded-xl font-semibold text-lg hover:bg-white/10 transition-all duration-300"
              >
                Learn More
              </Link>
            </div>
          </div>
          
          {/* Hero Image/Illustration */}
          <div className="relative hidden lg:block">
            <div className="relative w-full aspect-square max-w-lg mx-auto">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-blue-600 rounded-3xl transform rotate-6"></div>
              <div className="absolute inset-0 bg-white rounded-3xl p-8 shadow-2xl">
                <div className="grid grid-cols-2 gap-4 h-full">
                  <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-4 flex flex-col justify-center items-center text-white">
                    <Users className="w-12 h-12 mb-2" />
                    <span className="text-3xl font-bold">500+</span>
                    <span className="text-sm opacity-80">Members</span>
                  </div>
                  <div className="bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl p-4 flex flex-col justify-center items-center text-white">
                    <Calendar className="w-12 h-12 mb-2" />
                    <span className="text-3xl font-bold">50+</span>
                    <span className="text-sm opacity-80">Events</span>
                  </div>
                  <div className="bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl p-4 flex flex-col justify-center items-center text-white">
                    <Award className="w-12 h-12 mb-2" />
                    <span className="text-3xl font-bold">25+</span>
                    <span className="text-sm opacity-80">Awards</span>
                  </div>
                  <div className="bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl p-4 flex flex-col justify-center items-center text-white">
                    <Heart className="w-12 h-12 mb-2" />
                    <span className="text-3xl font-bold">1000+</span>
                    <span className="text-sm opacity-80">Impact</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" fill="white"/>
        </svg>
      </div>
    </section>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      icon: Users,
      title: 'Community Events',
      description: 'Regular workshops, seminars, and networking events to connect and learn.',
      color: 'bg-blue-500',
    },
    {
      icon: Calendar,
      title: 'Active Programs',
      description: 'Various programs designed to foster growth and development.',
      color: 'bg-amber-500',
    },
    {
      icon: Award,
      title: 'Recognition',
      description: 'Awards and recognition for outstanding contributions to the community.',
      color: 'bg-green-500',
    },
    {
      icon: Heart,
      title: 'Social Impact',
      description: 'Making a real difference through collective action and initiatives.',
      color: 'bg-red-500',
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Why Join ACTIV?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Be part of a community that's making waves. Here's what makes us special.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-6 bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-blue-100"
            >
              <div className={`w-14 h-14 ${feature.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const AboutPreview = () => {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="relative">
            <div className="aspect-[4/3] bg-gradient-to-br from-blue-600 to-blue-800 rounded-3xl overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <Target className="w-32 h-32 text-white/20" />
              </div>
            </div>
            <div className="absolute -bottom-6 -right-6 bg-white p-6 rounded-2xl shadow-xl">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Award className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">5+ Years</div>
                  <div className="text-sm text-gray-500">of excellence</div>
                </div>
              </div>
            </div>
          </div>
          
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              About Our Community
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              ACTIV is a community-driven organization committed to bringing together 
              individuals who share a common vision of creating positive change in society.
            </p>
            <p className="text-gray-600 mb-8">
              We believe in the power of collective action and strive to provide a platform 
              for members to connect, learn, and grow together. Our diverse community 
              encompasses people from all walks of life, united by a shared commitment to excellence.
            </p>
            
            <div className="grid grid-cols-2 gap-6 mb-8">
              <div className="text-center p-4 bg-blue-50 rounded-xl">
                <div className="text-3xl font-bold text-blue-600">500+</div>
                <div className="text-sm text-gray-600">Active Members</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-xl">
                <div className="text-3xl font-bold text-amber-600">50+</div>
                <div className="text-sm text-gray-600">Events Organized</div>
              </div>
            </div>
            
            <Link
              to="/about"
              className="inline-flex items-center text-blue-600 font-semibold hover:text-blue-700"
            >
              Learn more about us
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

const EventsPreview = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/events/?status=published&page_size=3`)
      .then((r) => r.json())
      .then((data) => {
        const results = data.results || data;
        if (Array.isArray(results) && results.length > 0) {
          setEvents(results.slice(0, 3));
        }
      })
      .catch(() => {});
  }, []);

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Upcoming Events
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Mark your calendars for these exciting upcoming events.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {events.length > 0 ? events.map((event) => (
            <div
              key={event.id}
              className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 overflow-hidden"
            >
              <div className="h-3 bg-gradient-to-r from-blue-500 to-blue-700"></div>
              <div className="p-6">
                <div className="inline-block px-3 py-1 bg-blue-100 text-blue-600 text-sm font-medium rounded-full mb-4">
                  {event.category || 'Event'}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {event.title}
                </h3>
                <p className="text-gray-600 mb-4 line-clamp-2">{event.description}</p>
                <div className="flex items-center text-gray-500 text-sm">
                  <Calendar className="w-4 h-4 mr-2" />
                  {event.event_date ? new Date(event.event_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }) : 'TBD'}
                </div>
              </div>
            </div>
          )) : [1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden animate-pulse">
              <div className="h-3 bg-blue-200"></div>
              <div className="p-6">
                <div className="h-4 bg-gray-200 rounded w-24 mb-4"></div>
                <div className="h-6 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-100 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <Link
            to="/events"
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all"
          >
            View All Events
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
};

const CTASection = () => {
  return (
    <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
          Ready to Make a Difference?
        </h2>
        <p className="text-xl text-blue-100 mb-8">
          Join our community today and be part of something meaningful. 
          Together, we can create positive change.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-all"
          >
            Become a Member
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
          <Link
            to="/contact"
            className="inline-flex items-center justify-center px-8 py-4 bg-transparent border-2 border-white/30 text-white rounded-xl font-semibold text-lg hover:bg-white/10 transition-all"
          >
            Contact Us
          </Link>
        </div>
      </div>
    </section>
  );
};

const Home = () => {
  return (
    <div>
      <HeroSection />
      <FeaturesSection />
      <AboutPreview />
      <EventsPreview />
      <CTASection />
    </div>
  );
};

export default Home;
