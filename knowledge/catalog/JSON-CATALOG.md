# Catálogo de formatos JSON bajo analysis/ (generado, no editar a mano)

Total archivos: 2146. Familias (firmas estructurales) distintas: 108.
Inválidos/no legibles: 0. Vacíos: 0.

Una firma agrupa por FORMA (claves+tipos), no por significado: dos familias con claves parecidas pueden representar cosas distintas; revisar `sample_paths` antes de asumir equivalencia semántica.

## Familias por tamaño (archivos), con pista de evidencia técnica aprovechable

| # archivos | tamaño total | con pista evidencia | forma | claves | ejemplo |
|---|---|---|---|---|---|
| 641 | 9193290 | no | dict | class, diagnostics, elf_type, exports, imports, kernel_module, machine, needed, runpath, soname | `analysis/elf-cache/0c3931ebc996851a9fa4f838bb4f9640d8a165c78b1047d564274bff7b7105a6-002a27abd9ab4b0f1345a002cc768834a2e8f0578dd2b7b6e222ae01bd6810c7.json` |
| 641 | 9208695 | no | dict | class, diagnostics, elf_type, exports, imports, interpreter, kernel_module, machine, needed, runpath, soname | `analysis/elf-cache/6870c19293b708bdd4649acf1a0c60c9d8c3b792f3d8e94e8f638c32d19e2a8d-002a27abd9ab4b0f1345a002cc768834a2e8f0578dd2b7b6e222ae01bd6810c7.json` |
| 248 | 2469560 | no | dict | constant_memory_assumption, firmware_profile, functions, method, source_sha256, source_size | `analysis/ghidra/a6000-all-exposure-sequences.json` |
| 118 | 665087 | no | list_of_dict | entry, pseudo_code, status | `analysis/ghidra/branch-claude-effect-parser.json` |
| 89 | 365628 | no | dict | functions, language, method, rom_base, source_sha256 | `analysis/ghidra/a6000-darwin-adc-phase-notification.json` |
| 61 | 109092 | no | dict | coverage, function_count, targets | `analysis/ghidra/a6300-caif-sio-channel-references.json` |
| 59 | 1220955 | no | dict | constant_memory_assumption, functions, method, source_sha256 | `analysis/ghidra/capture-exposure-mode-gate.json` |
| 29 | 1020184 | no | dict | library, reused, rtti, sha256_after, sha256_before, windows | `analysis/session21/evidence/codex-dcf-publication-tail.json` |
| 29 | 505969 | no | list_of_dict | entry, pseudo_code, query, status | `analysis/session22/evidence/s29-mpr-completion.json` |
| 22 | 3395539 | SÍ | dict | callers, library, literals, outgoing, plt, references, rtti, sha256, symbols, virtuals, window_owners, windows | `analysis/session20/evidence/codex-dcf-actual-write.json` |
| 17 | 359308 | no | dict | branch_candidates, library, reused, rtti, sha256_after, sha256_before, target_relocations, target_virtuals, windows | `analysis/session21/evidence/codex-command9-followup.json` |
| 12 | 266444 | no | dict | functions, method, source_sha256 | `analysis/ghidra/silent-alias-proof.json` |
| 12 | 2345118 | no | dict | artifacts, captures, environments, providers, records, scenarios, unknowns | `analysis/rea/CautionConfig-evidence.json` |
| 12 | 6141378 | no | dict | binding, entries, evidence_bundle, target, workflow_entries | `analysis/rea/CautionConfig.snapshot.json` |
| 10 | 86363 | no | dict | runs, session | `analysis/session19/codex-runs/run-001/orchestration/codex-continuous-ledger.json` |
| 10 | 65241 | no | list_of_dict | effort_requested, errors, files_created, files_modified, finish_reason, model_requested, next_task_available, next_task_id, run_number, status, task_id | `analysis/session19/codex-runs/run-001/orchestration/progress.json` |
| 9 | 17646 | no | dict | functions, language, method, source_sha256 | `analysis/ghidra/a6000-darwin-shutter-adc-inventory.json` |
| 9 | 58170 | no | dict | functions, image_bias, limitation, method, source_sha256 | `analysis/ghidra/a6300-shared-queue-producers.json` |
| 7 | 15623 | no | dict | cases, entry, limitation, method, passed, source_sha256 | `analysis/ghidra/a6000-mode-emulation-verified.json` |
| 5 | 35418 | no | dict | analysis_profile, authority, confidence, environment, evidence_id, evidence_links, limitations, locations, normalized_result, operation, parameters, predicate_type … | `analysis/functions/rea-takePicture-decompile.json` |
| 3 | 7771 | no | dict | binary_sha256, findings, firmware, method, run_number, safety, session, task_id | `analysis/session19/codex-runs/run-002/evidence/lifecycle-connect.json` |
| 3 | 6250625 | no | dict | classes, methods_by_entry | `analysis/session20/evidence/libBizFw-rtti-vtables.json` |
| 2 | 2932 | no | dict | examples, failures, limitation, model, passed, passed_cases, source_sha256, start, stop_before, total_cases | `analysis/ghidra/a6000-darwin-capture-bit-emulation.json` |
| 2 | 2902 | no | dict | callback_pointer_occurrences, function, instruction_window_hex, limitations, method, model, phase_destinations, rom_base, source_sha256, status, table, table_hex … | `analysis/ghidra/a6000-darwin-phase-table-verified.json` |
| 2 | 30869 | no | dict | content, structuredContent | `analysis/ghidra/a6300-kikilog-acm-rea.json` |
| 2 | 5546 | no | dict | conclusion, findings, next_task, run_number, scope, session, silent_shutter_functional, status, task_id | `analysis/session19/codex-runs/run-001/evidence/s2-domain-bridge.json` |
| 2 | 9012 | SÍ | dict | binary, compatibility, findings, method, safety, scope, task_id, verdict | `analysis/session19/codex-runs/run-005/evidence/camera-effect-sdf.json` |
| 2 | 4954 | no | dict | findings, firmware, method, run_number, safety, session, task_id | `analysis/session19/codex-runs/run-006/evidence/fea-callback-completion.json` |
| 2 | 8276 | no | dict | findings, firmware, method, run_number, safety, session, state_separation, task_id | `analysis/session19/codex-runs/run-008/evidence/dcf-playback-completion.json` |
| 2 | 5554 | no | dict | findings, firmware, method, next_task, next_task_id, run_number, safety, session, status, task_id | `analysis/session19/codex-runs/run-009/evidence/camerasequence-sdcom.json` |
| 2 | 7390 | no | dict | delivery, findings, next_task, next_task_id, safety, scope, status, task_id, term_sfra, unverified | `analysis/session19/codex-runs/run-010/evidence/sfra-yc-linux-delivery.json` |
| 2 | 6058 | SÍ | dict | binary, findings, method, next_task, next_task_id, safety, scope, task_id, verdict | `analysis/session19/codex-runs/run-011/evidence/objeffect-modes-2-5.json` |
| 2 | 7238 | no | dict | findings, method, next_task, next_task_id, safety, scope, status, task_id | `analysis/session19/codex-runs/run-012/evidence/mechanical-shutter-decision-points.json` |
| 2 | 139639 | SÍ | dict | callers, library, plt, references, rtti, sha256, symbols, virtuals, windows | `analysis/session20/evidence/codex-dcf-media.json` |
| 2 | 81507 | SÍ | dict | callers, library, plt, references, sha256, symbols, virtuals, windows | `analysis/session20/evidence/codex-dcf-mpr-initial.json` |
| 2 | 9276 | no | dict | 0x230c20, 0x23b654, 0x250574, 0x319308, 0x333f40, 0x36343e, 0x373478, 0x385054, 0x3965f4, 0x39dee0, 0x3aca58, 0x3fa39e … | `analysis/session20/evidence/libObj-pin-signatures.json` |
| 1 | 2051 | no | dict | announcement, av_cam, download_url, embedded_dat, excluded_comparison, firmware_version, installer, libObj, model, purpose, retrieved_date, silent_shooting_manual … | `analysis/a6300-source.json` |
| 1 | 9495 | no | list_of_dict | clasificacion, descripcion, direccion_elf, evidencia, item | `analysis/branch-claude-effect-states.json` |
| 1 | 6732 | no | dict | conclusion, dmm_share, geometry_and_sdf, ownership_lifetime, pbcap_buffers, producer_chain, rejected_claims, scope, sds_header | `analysis/branch-codex-yc-memory.json` |
| 1 | 2669 | no | dict | config_data, extents, format_inference, scope, unit_type_mapping | `analysis/dmm-extent-sizes.json` |
| 1 | 10598 | no | dict | count, known, unit_types | `analysis/dmm-unit-types.json` |
| 1 | 6435 | no | dict | alcance, cadena, clasificacion, correcciones_sesiones_previas, evidencias, modos_record_image, sesion, veredicto | `analysis/encodestill-command-flow.json` |
| 1 | 8796 | no | dict | alcance, correccion_sesion_14, encode_still_param_8_palabras, mensaje_entrada_execute, no_hay_validacion_de, propiedad_y_vida_util, region_info_0x40, resumen, semantica_unitType, sesion, tamanos_salida, transporte_a_libmpr … | `analysis/encodestill-yc-contract.json` |
| 1 | 2185 | SÍ | list_of_dict | address_space, binary, confidence, incoming, instruction_address, original_name, outgoing, pending, sha256, symbol_value, variables | `analysis/functions/dossiers.json` |
| 1 | 1436 | SÍ | dict | accepted_message_ids, binary, binary_sha256, candidate_elf_entry, candidate_ghidra_entry, confidence, date, ghidra_string_reference_site, hardware_support, id, incoming_references, limitations … | `analysis/functions/silent-shutter-converter.json` |
| 1 | 4470 | no | dict | address_space, backend, board_defaults, date, handler, header_normalization, independent_osal_evidence, limits, registration, source_sha256, status | `analysis/ghidra/a6300-caif-sio-endpoint-checkpoint.json` |
| 1 | 9910 | no | dict | functions, method, raw_base, source_sha256 | `analysis/ghidra/a6300-imx284-readout-helpers.json` |
| 1 | 3928 | no | dict | date, dma_source, gpio_map, inhibit_error_mask, interrupt_dispatch, method, next, rom_base, source_sha256, status | `analysis/ghidra/darwin-dma-gpio-checkpoint.json` |
| 1 | 14132 | no | dict | a6000_source_sha256, a6300_source_sha256, emulation, evidence, inference, not_verified, scope, verified_a6000, verified_a6300, verified_efcs_packet_bridge, verified_liro_peer_handshake | `analysis/ghidra/darwin-mechanical-enable-checkpoint.json` |
| 1 | 2895 | no | list_of_dict_variant | entry, pseudo_code, status | `analysis/ghidra/dataflow-sendasync.json` |
| 1 | 1141 | no | dict | policy, queries, source_sha256 | `analysis/ghidra/rejected-queries.json` |
| 1 | 12918 | no | dict | base, functions, method, source_sha256 | `analysis/ghidra/silent-liro-functions.json` |
| 1 | 7167 | SÍ | dict | ctor_stack_args, elf, modes | `analysis/imx210-drvparam-inputs.json` |
| 1 | 11119 | SÍ | dict | modes, rows | `analysis/imx210-setmode-register-matrix.json` |
| 1 | 10846 | no | dict | contradicciones, fuentes, hallazgos_nuevos_cruzados, incidente, metodo, nota_contradicciones, respuestas_informe_final, sesion | `analysis/liveview-encodestill-crosscheck.json` |
| 1 | 10261 | no | dict | bloque_0xB0, consumidor, equivalencia_12B, estado, evidencias, item_0x100E, items_0x100C_0x100D, no_verificado, nota_direcciones, productor, sentinelas_y_errores, sesion … | `analysis/objstillpool-100b-layout.json` |
| 1 | 2222 | no | dict | architecture, blocked, classification_mode4, graph, objects, session, wsi_param_layout | `analysis/objstillrecorder-mode4-flow.json` |
| 1 | 2241 | no | dict | blocked_pending, getfileimage_class, message_0x3a48, minimum_contract_for_mpr, new_functions, recommended_architecture, recordStillImage_0x1027, record_offsets_0x30_0x3c, session, thumbnail_screennail_producer | `analysis/record-image-completion-flow.json` |
| 1 | 1196 | no | dict | addr_note, conclusion, functions, record_offsets, session, unverified | `analysis/record-still-image-flow.json` |
| 1 | 9061 | no | dict | alcance, escritor_tabla_1025, escritores_modo1, escritores_reset_modo1_a_0, hallazgo_principal, limitaciones, metodo, respuesta_a_la_tarea_A1, sesion | `analysis/s16-claude-effect-mode1.json` |
| 1 | 10002 | no | dict | A2_1_modelos_que_crean_fila_0x2a, A2_2_construccion_dinamica_de_listas, A2_3_combinacion_0x0a_0x07_0x2a_en_misma_secuencia, A2_4_transiciones_hacia_modelos_de_grabacion, A2_5_otros_usos_de_stsid_6, A2_6_conexiones_temporales_crear_destruir_misma_secuencia, A2_7_otras_creaciones_de_0x2a_fuera_de_pbcap_edicion, alcance, cobertura_real, discrepancia_conteo, ids_literales_encontrados_create, ids_literales_encontrados_destroy … | `analysis/s16-claude-topology-audit.json` |
| 1 | 4645 | no | dict | addressing, binaries, camera_yc, commands, encode_still, ownership, pbcap, scope | `analysis/s16-codex-camera-yc.json` |
| 1 | 13542 | no | dict | contradicciones, fuentes, hallazgos_nuevos_cruzados, metodo, nota_contradicciones, respuestas_informe_final, sesion, verificacion_cruzada_critica | `analysis/s16-liveview-recorder-crosscheck.json` |
| 1 | 15880 | no | dict | agente, alcance, clasificacion_global, correccion_metodologica, dato_para_codex_c, decompilados, evidencia_cruda, hallazgo_central, proceso, respuestas_10_preguntas, sesion, siguiente_bloqueo | `analysis/s17-claude-a-topology.json` |
| 1 | 11971 | no | dict | agent, findings, local_evidence_files, message_for_principal_claude, mission, process_confirmation, session, sources_fetched_real | `analysis/s17-claude-b-api-native-flow.json` |
| 1 | 3005 | no | dict | addressing, camera, geometry, memory_contract, playdata, scope, sdf, sequence_6013, verdict | `analysis/s17-codex-c-yc-contract.json` |
| 1 | 2229 | SÍ | dict | binaries, callback, completion_to_dcf, encodestill, external_context, memory, scope | `analysis/s17-codex-d-fea-callback.json` |
| 1 | 12993 | no | dict | alcance, configuracion_real, contradicciones, fuentes, hallazgos_nuevos_cruzados, metodo, nota_contradicciones, respuestas_informe_final, sesion, verificacion_cruzada_critica | `analysis/s17-parallel-crosscheck.json` |
| 1 | 1499 | no | dict | cases, got_base | `analysis/seq-dispatch-table.json` |
| 1 | 9959 | no | dict | claims_silentshutter_works, context_md_not_edited, effort_note, effort_requested, findings, model_match, model_requested, model_used, no_binary_modification, no_device_connection, no_subagents_used, scope … | `analysis/session18/claude-a/s18-claude-a-lifecycle.json` |
| 1 | 10359 | no | dict | answers, branch, classification_legend, disclaimer, incidents, model_effort_actually_used, scope, session, sources | `analysis/session18/claude-b/s18-claude-b-camerasequence.json` |
| 1 | 7217 | no | dict | incidents, load_base_liro_verified, methodological_note_thumb_bit, model_effort_declared, next_session_open_items, question_1_dynamic_rows, question_2_queue_0x40193_consumer, question_3_kernel_primitives, question_4_gpio_irq_handler_for_s2, questions_5_to_14_consolidated_chain, rules_followed, scope … | `analysis/session18/claude-c/s18-claude-c-relmgr.json` |
| 1 | 8695 | no | dict | binaries, classification_legend, effort_used, files_touched, findings, incidents, method, model_used, requested, rules_followed, session, silent_shutter_disclaimer … | `analysis/session18/claude-d/s18-claude-d-topology.json` |
| 1 | 4987 | no | dict | agent, artifacts, constraints_observed, findings, kernel_crossing_rule, scope, session, silent_shutter | `analysis/session18/codex-e/s18-codex-e-yc-buffers.json` |
| 1 | 6150 | no | dict | addressing, conclusion, findings, safety_conclusion, scope | `analysis/session18/codex-f/s18-codex-f-sdf-yc.json` |
| 1 | 5773 | no | dict | final_boundary, findings, safety, scope, session, source_archive | `analysis/session18/codex-g/s18-codex-g-fea-dmm.json` |
| 1 | 4592 | no | dict | agent, artifacts, findings, safety_statement, scope, session | `analysis/session18/codex-h/s18-codex-h-mpr-dcf.json` |
| 1 | 8720 | no | dict | alcance, bloqueos_siguiente_sesion, configuracion_real, contradicciones, correcciones_cruzadas, criterios_exito, fecha, hallazgos_nuevos_por_rama, limite_2claude_2codex_x2, metodo, que_aporto_sony_oss, sesion … | `analysis/session18/main/s18-parallel-crosscheck.json` |
| 1 | 5557 | no | dict | advertencia, archivos, comparacion_a6000_vs_a6300, fecha_inventario, hallazgos_kernel_relevantes, limitaciones_declaradas, sesion, ubicacion_extraccion, ubicacion_originales | `analysis/session18/main/sony-oss-inventory.json` |
| 1 | 3328 | SÍ | dict | binary, camera_contract, findings, safety, scope, task_id, verdict | `analysis/session19/codex-runs/run-004/camera-yc-contract.json` |
| 1 | 294 | no | dict | copy_of, status, summary, task_id | `analysis/session19/codex-runs/run-013/post-s2-cancellation-states.json` |
| 1 | 3867 | SÍ | dict | binary, camera_contract, findings, method, safety, scope, task_id, verdict | `analysis/session19/evidence/camera-yc-contract.json` |
| 1 | 4216 | no | dict | already_analyzed, discarded, findings, firmware, load_base, method, pending_confirmed, safety, table_initializer, task_id | `analysis/session19/evidence/liro-remaining-sequences.json` |
| 1 | 2622 | SÍ | dict | binary, binary_sha256, findings, firmware, method, run_number, safety, session, task_id | `analysis/session19/evidence/objid53-registration.json` |
| 1 | 3115 | no | dict | findings, firmware, method, next_task, next_task_id, safety, scope, status, task_id | `analysis/session19/evidence/post-s2-cancellation-states.json` |
| 1 | 55093 | no | list_of_dict_variant | agent, architecture, blockers, checks_performed, date, discarded_hypotheses, evidence, files_created, files_modified, findings, id, next_task_selected … | `analysis/session20/checkpoints/progress.json` |
| 1 | 5545 | no | dict | creators, no_static_list_contains_0xb4, objscalar_getpin6, scope, sequence_still_capture_start, session, topology_list_format | `analysis/session20/evidence/claude-topology-ae-b4-sequence.json` |
| 1 | 4522 | no | dict | all_named_relocations, checks, classification, hashes, import_export_scan, limits, public_api_targets, result, valid_evidence_json_count, vtable_slots | `analysis/session20/evidence/codex-dcf-audit.json` |
| 1 | 54 | no | dict | 0x42bfc | `analysis/session20/evidence/libBizFw-pin-signatures.json` |
| 1 | 54 | no | dict | 0x2bfc0 | `analysis/session20/evidence/libBizFw2-pin-signatures.json` |
| 1 | 1404 | no | list_of_dict | call, name, r1 | `analysis/session20/evidence/libobj-objactivebase-calls.json` |
| 1 | 80878 | no | dict | function_starts, results | `analysis/session20/evidence/libobj-send-owners.json` |
| 1 | 5427 | no | dict | central_question_answer, firmware, no_binaries_modified, no_codex_no_subagents, silentshutter_functional, status, strings_checked, task_id, tool, verified_functions | `analysis/session20/evidence/rawplay-stage-reuse.json` |
| 1 | 126 | no | dict | hits, note | `analysis/session20/evidence/s20-scalar-40193.json` |
| 1 | 3363 | no | dict | all_rows, classification, known_dispatcher_438052d8, literal_0x4044_search_false_positive, row_count, row_format, table_end, table_start, target_entry, task | `analysis/session20/evidence/s20-table-0x4044-registration.json` |
| 1 | 2866 | no | dict | avcam, darwin, input_ko, libobj, schematic_a6000_service_L3 | `analysis/session21/evidence/claude-button-to-shutter.json` |
| 1 | 31832 | no | dict | checks, limits, recstill_vtable, result, stage_notify_reused_listing | `analysis/session21/evidence/codex-chain-audit.json` |
| 1 | 79331 | no | dict | analysis_top_level, required_documents, trees | `analysis/session21/evidence/codex-inventory.json` |
| 1 | 741 | no | dict | architecture, audit, evidence_json_valid, git_repository, own_scripts, production_calls, report_links_valid, requested_checks, status, subagents | `analysis/session21/evidence/codex-validation.json` |
| 1 | 1468 | no | dict | audit, date, firmware_execution, git, hardware_access, limits, mypy, original_libraries, packages_installed, ruff, scope | `analysis/session22/evidence/s29-validation.json` |
| 1 | 29275 | no | dict | hashes, windows | `analysis/session22/evidence/s30-native-verified.json` |
| 1 | 845 | no | dict | functional_closure, git, mypy_new_auditor, mypy_src, ruff_new_auditor, ruff_src_tests, s28_dataflow_contract_audit, s29_writestill_audit, s30_pipeline_audit, scope, verdict | `analysis/session22/evidence/s30-validation.json` |
| 1 | 1006 | no | dict | anclas_golpeadas, destinos, region | `analysis/sfra-outcalls.json` |
| 1 | 539810 | SÍ | dict | address_convention, answers, completion, control, corrections, date, date_layout, descriptor_format, evidence, firmware, gps_layout, handle_domains … | `analysis/stillinfo-layout.json` |
| 1 | 143065 | SÍ | list_of_dict | hits, path, sha256 | `analysis/strings/keyword-hits.json` |
| 1 | 19924 | SÍ | list_of_dict | expected_size, hits, path, physical, sha256, size, virtual | `analysis/strings/wbi-keyword-hits.json` |
| 1 | 38347 | no | dict | obj_tbl_libsysdef, pin_tbl, topology_rows | `analysis/topology-table-libobj.json` |
| 1 | 8495 | no | dict | NO_VERIFICADO, alcance, errores_y_timeout, identidad_objetos, playdata_producido, propiedad_y_liberacion, respuesta_pregunta_decisiva, sesion, trazado, veredicto | `analysis/yc-pin-delivery-flow.json` |
