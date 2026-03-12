import React from 'react';
import { Link } from 'react-router-dom';
import { Target, Eye, Heart, Users, Award, TrendingUp, ArrowRight } from 'lucide-react';

const About = () => {
  const stats = [
    { value: '500+', label: 'Active Members' },
    { value: '50+', label: 'Events Organized' },
    { value: '5+', label: 'Years of Excellence' },
    { value: '25+', label: 'Awards Won' },
  ];

  const values = [
    {
      icon: Heart,
      title: 'Integrity',
      description: 'We uphold the highest ethical standards in all our actions and decisions.',
    },
    {
      icon: Users,
      title: 'Community',
      description: 'We believe in the power of togetherness and mutual support.',
    },
    {
      icon: Award,
      title: 'Excellence',
      description: 'We strive for excellence in everything we do.',
    },
    {
      icon: TrendingUp,
      title: 'Growth',
      description: 'We are committed to continuous learning and personal development.',
    },
  ];

  const team = [
    {
      name: 'Dr. Rajesh Kumar',
      role: 'President',
      image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop',
    },
    {
      name: 'Sarah Johnson',
      role: 'Vice President',
      image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop',
    },
    {
      name: 'Michael Chen',
      role: 'Secretary',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop',
    },
    {
      name: 'Priya Sharma',
      role: 'Treasurer',
      image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop',
    },
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              About ACTIV
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Building a stronger community through collaboration, excellence, and shared vision.
            </p>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-8 rounded-3xl">
              <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-6">
                <Target className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h2>
              <p className="text-gray-600 text-lg">
                To create a vibrant, inclusive community that fosters personal growth, 
                professional development, and social impact. We aim to bring together 
                individuals who are passionate about making a positive difference in society.
              </p>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 p-8 rounded-3xl">
              <div className="w-16 h-16 bg-amber-500 rounded-2xl flex items-center justify-center mb-6">
                <Eye className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Vision</h2>
              <p className="text-gray-600 text-lg">
                To be the leading community organization that empowers individuals to 
                achieve their full potential and contribute meaningfully to society. 
                We envision a world where community spirit drives positive change.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Core Values
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              These values guide everything we do as a community.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div
                key={index}
                className="text-center p-6 rounded-2xl hover:bg-gray-50 transition-colors"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <value.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{value.title}</h3>
                <p className="text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Meet Our Team
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              The dedicated individuals leading our community forward.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className="aspect-square bg-gray-200">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6 text-center">
                  <h3 className="text-xl font-semibold text-gray-900">{member.name}</h3>
                  <p className="text-gray-600">{member.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Join Our Community
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Be part of something meaningful. Connect with like-minded individuals and make a difference.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-all"
          >
            Become a Member
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default About;
