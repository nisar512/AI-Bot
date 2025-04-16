import React, { Suspense } from 'react'
import ChatWindow from '@/components/Chat/chat'

const ChatPage = () => {
  return (
    <div className='w-full h-full'>
      <Suspense fallback={<div>Loading chat...</div>}>
        <ChatWindow />
      </Suspense>
    </div>
  )
}

export default ChatPage
