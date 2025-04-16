import React, { Suspense } from 'react'
import ChatWindow from '@/components/Chat/chat'
import { Skeleton } from '@/components/ui/skeleton'

const ChatPage = () => {
  return (
    <div className='w-full h-full'>
      <Suspense fallback={<Skeleton className="h-10  w-[80%] mx-auto bg-muted-foreground/20" />}>
        <ChatWindow />
      </Suspense>
    </div>
  )
}

export default ChatPage
