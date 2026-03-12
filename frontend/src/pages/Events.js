import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Clock, Users, ArrowRight, Filter } from 'lucide-react';

const Events = () => {
  const [activeFilter, setActiveFilter] = useState('all');

  const filters = [
    { id: 'all', label: 'All Events' },
    { id: 'networking', label: 'Networking' },
    { id: 'workshop', label: 'Workshop' },
    { id: 'social', label: 'Social' },
    { id: 'seminar', label: 'Seminar' },
  ];

  const events = [
    {
      id: 1,
      title: 'Annual Community Meetup 2026',
      description: 'Join us for our biggest annual gathering where we celebrate achievements and set new goals. Network with fellow members and enjoy insightful sessions.',
      date: 'March 15, 2026',
      time: '10:00 AM - 5:00 PM',
      location: 'Community Hall, New Delhi',
      category: 'networking',
      attendees: 120,
      image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&h=400&fit=crop',
    },
    {
      id: 2,
      title: 'Leadership Excellence Workshop',
      description: 'A comprehensive workshop on developing essential leadership skills. Learn from industry experts and enhance your leadership capabilities.',
      date: 'April 5, 2026',
      time: '2:00 PM - 6:00 PM',
      location: 'Training Center, Mumbai',
      category: 'workshop',
      attendees: 45,
      image: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=400&fit=crop',
    },
    {
      id: 3,
      title: 'Community Service Day',
      description: 'Give back to the community through various service activities. Together we can make a difference in the lives of those in need.',
      date: 'April 20, 2026',
      time: '8:00 AM - 2:00 PM',
      location: 'Various Locations',
      category: 'social',
      attendees: 80,
      image: 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=800&h=400&fit=crop',
    },
    {
      id: 4,
      title: 'Tech Trends Seminar',
      description: 'Explore the latest technology trends and their impact on businesses. Featuring talks from industry leaders and innovators.',
      date: 'May 10, 2026',
      time: '11:00 AM - 4:00 PM',
      location: 'Tech Park, Bangalore',
      category: 'seminar',
      attendees: 150,
      image: 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=800&h=400&fit=crop',
    },
    {
      id: 5,
      title: 'Professional Networking Evening',
      description: 'Connect with professionals from various industries. Share experiences and build valuable connections.',
      date: 'May 25, 2026',
      time: '6:00 PM - 9:00 PM',
      location: 'Hotel Grand, Chennai',
      category: 'networking',
      attendees: 60,
      image: 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&h=400&fit=crop',
    },
    {
      id: 6,
      title: 'Skill Development Workshop',
      description: 'Enhance your professional skills with hands-on training sessions. Topics include communication, time management, and more.',
      date: 'June 15, 2026',
      time: '10:00 AM - 4:00 PM',
      location: 'Learning Center, Hyderabad',
      category: 'workshop',
      attendees: 35,
      image: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&h=400&fit=crop',
    },
  ];

  const filteredEvents = activeFilter === 'all' 
    ? events 
    : events.filter(event => event.category === activeFilter);

  const getCategoryColor = (category) => {
    const colors = {
      networking: 'bg-blue-100 text-blue-700',
      workshop: 'bg-amber-100 text-amber-700',
      social: 'bg-green-100 text-green-700',
      seminar: 'bg-purple-100 text-purple-700',
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Our Events
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Join our events to connect, learn, and grow with like-minded individuals.
            </p>
          </div>
        </div>
      </section>

      {/* Filters */}
      <section className="py-8 bg-white border-b sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 overflow-x-auto pb-2">
            <Filter className="w-5 h-5 text-gray-500 flex-shrink-0" />
            {filters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setActiveFilter(filter.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  activeFilter === filter.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Events Grid */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 group"
              >
                <div className="relative h-48 overflow-hidden">
                  <img
                    src={event.image}
                    alt={event.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute top-4 left-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(event.category)}`}>
                      {event.category.charAt(0).toUpperCase() + event.category.slice(1)}
                    </span>
                  </div>
                </div>
                
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {event.title}
                  </h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">
                    {event.description}
                  </p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-gray-500 text-sm">
                      <Calendar className="w-4 h-4 mr-2" />
                      {event.date}
                    </div>
                    <div className="flex items-center text-gray-500 text-sm">
                      <Clock className="w-4 h-4 mr-2" />
                      {event.time}
                    </div>
                    <div className="flex items-center text-gray-500 text-sm">
                      <MapPin className="w-4 h-4 mr-2" />
                      {event.location}
                    </div>
                    <div className="flex items-center text-gray-500 text-sm">
                      <Users className="w-4 h-4 mr-2" />
                      {event.attendees} attending
                    </div>
                  </div>
                  
                  <Link
                    to="/register"
                    className="inline-flex items-center justify-center w-full px-4 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors"
                  >
                    Register Now
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
          
          {filteredEvents.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No events found in this category.</p>
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Want to Organize an Event?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            We welcome event proposals from our community members. Let's create something amazing together.
          </p>
          <Link
            to="/contact"
            className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold text-lg hover:bg-blue-700 transition-all"
          >
            Contact Us
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Events;
