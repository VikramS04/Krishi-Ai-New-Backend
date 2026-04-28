const mongoose = require('mongoose')

let cached = global.mongoose

if (!cached) {
  cached = global.mongoose = { conn: null, promise: null }
}

const connectDB = async () => {
  if (cached.conn) {
    return cached.conn
  }

  const mongoUri = process.env.MONGODB_URI
  if (!mongoUri) {
    throw new Error('Missing MONGODB_URI environment variable')
  }

  if (!cached.promise) {
    cached.promise = mongoose.connect(mongoUri, {
      bufferCommands: false,
      serverSelectionTimeoutMS: 5000,
    }).then((instance) => instance)
  }

  try {
    cached.conn = await cached.promise
    console.log('MongoDB Connected')
    return cached.conn
  } catch (error) {
    cached.promise = null
    throw error
  }
}

mongoose.connection.on('disconnected', () => {
  console.warn('MongoDB disconnected')
})

module.exports = connectDB
