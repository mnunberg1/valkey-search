/*
 * Copyright (c) 2025, valkey-search contributors
 * All rights reserved.
 * SPDX-License-Identifier: BSD 3-Clause
 *
 */

#pragma once

#include "google/protobuf/arena.h"
#include "grpcpp/support/message_allocator.h"

// 'src' is misleading here; this is actually in the build output directory
#include "src/coordinator/coordinator.pb.h"

#include <valkey/valkey_module.h>

namespace valkey_search::coordinator {

// Options for a protobuf Arena whose block source is ValkeyModule_Alloc/Free.
//
// Arena sub-allocates fields -- repeated/submessage fields and string/bytes
// payloads alike -- via placement-new directly into its own blocks, bypassing
// `new`/`operator new` entirely. Left at its defaults, an Arena's blocks come
// from plain system malloc, invisible to Valkey's allocator. Used by both the
// coordinator client (client.cc) and server (ValkeyMessageAllocator below)
// for any request/response with meaningful cardinality or mass.
inline google::protobuf::ArenaOptions MakeValkeyArenaOptions() {
  google::protobuf::ArenaOptions options;
  options.block_alloc = [](size_t size) { return ValkeyModule_Alloc(size); };
  options.block_dealloc = [](void* ptr, size_t) { ValkeyModule_Free(ptr); };
  return options;
}

// Without a custom MessageAllocator, gRPC's callback unary handler allocates
// each call's request/response messages out of grpc-core's own per-call
// arena (see DefaultMessageHolder in grpcpp/impl/server_callback_handlers.h),
// which is a C-level (gpr_malloc-backed) arena that Valkey's allocator never
// sees. Registering one of these via
// <Service>::SetMessageAllocatorFor_<Method>() routes the top-level
// request/response allocation through ValkeyModule_Alloc/Free instead.
//
// Request/response are Arena-backed (not just placement-new'd once) so that
// every field -- repeated/submessage fields and string/bytes payloads alike
// -- is also explicitly routed through ValkeyModule_Alloc, regardless of
// cardinality (e.g. SearchIndexPartitionResponse's per-neighbor,
// per-attribute entries) or mass (e.g. SearchIndexPartitionRequest's `bytes
// query`, AttributeContentEntry's `content`). This does not rely on this
// project's global operator new/delete override
// (vmsdk/src/memory_allocation_overrides.cc) as a safety net: that override
// is a symbol-interposition trick that only works reliably under static
// linking (see CLAUDE.md) and is meant to go away, so anything that can be
// allocated at meaningful mass or cardinality needs an explicit
// ValkeyModule_XXX-backed path of its own rather than depending on it.
template <typename RequestT, typename ResponseT>
class ValkeyMessageAllocator final
    : public grpc::MessageAllocator<RequestT, ResponseT> {
 public:
  grpc::MessageHolder<RequestT, ResponseT>* AllocateMessages() override {
    return new (ValkeyModule_Alloc(sizeof(Holder))) Holder();
  }

 private:
  class Holder final : public grpc::MessageHolder<RequestT, ResponseT> {
   public:
    Holder() : arena_(MakeValkeyArenaOptions()) {
      this->set_request(google::protobuf::Arena::Create<RequestT>(&arena_));
      this->set_response(google::protobuf::Arena::Create<ResponseT>(&arena_));
    }

    void Release() override {
      this->~Holder();
      ValkeyModule_Free(this);
    }

   private:
    google::protobuf::Arena arena_;
  };
};


struct MessageAllocators {
private:
  ValkeyMessageAllocator<GetGlobalMetadataRequest, GetGlobalMetadataResponse> get_global_metadata;
  ValkeyMessageAllocator<SearchIndexPartitionRequest, SearchIndexPartitionResponse> search_index_partition;
  ValkeyMessageAllocator<InfoIndexPartitionRequest, InfoIndexPartitionResponse> info_index_partition;
  static MessageAllocators instance;

public:
  class Use {
  public:
    template <typename S>
    explicit Use(S* service) {
      service->SetMessageAllocatorFor_GetGlobalMetadata(&instance.get_global_metadata);
      service->SetMessageAllocatorFor_SearchIndexPartition(&instance.search_index_partition);
      service->SetMessageAllocatorFor_InfoIndexPartition(&instance.info_index_partition);
    }
  };
};



}  // namespace valkey_search::coordinator
