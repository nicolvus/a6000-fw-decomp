# Catálogo de formatos JSON bajo analysis/ (generado, no editar a mano)

Total archivos: 2990. Familias (firmas estructurales) distintas: 543.
Inválidos/no legibles: 0. Vacíos: 12.

Una firma agrupa por FORMA (claves+tipos), no por significado: dos familias con claves parecidas pueden representar cosas distintas; revisar `sample_paths` antes de asumir equivalencia semántica.

## Familias por tamaño (archivos), con pista de evidencia técnica aprovechable

| # archivos | tamaño total | con pista evidencia | forma | claves | ejemplo |
|---|---|---|---|---|---|
| 641 | 9193290 | no | dict | class, diagnostics, elf_type, exports, imports, kernel_module, machine, needed, runpath, soname | `analysis/elf-cache/0c3931ebc996851a9fa4f838bb4f9640d8a165c78b1047d564274bff7b7105a6-002a27abd9ab4b0f1345a002cc768834a2e8f0578dd2b7b6e222ae01bd6810c7.json` |
| 641 | 9208695 | no | dict | class, diagnostics, elf_type, exports, imports, interpreter, kernel_module, machine, needed, runpath, soname | `analysis/elf-cache/6870c19293b708bdd4649acf1a0c60c9d8c3b792f3d8e94e8f638c32d19e2a8d-002a27abd9ab4b0f1345a002cc768834a2e8f0578dd2b7b6e222ae01bd6810c7.json` |
| 257 | 2707902 | no | dict | constant_memory_assumption, firmware_profile, functions, method, source_sha256, source_size | `analysis/ghidra/a6000-all-exposure-sequences.json` |
| 118 | 665087 | no | list_of_dict | entry, pseudo_code, status | `analysis/ghidra/branch-claude-effect-parser.json` |
| 97 | 7192017 | SÍ | dict | functions, sha256 | `analysis/ghidra/s40-snapshots.json` |
| 89 | 365628 | no | dict | functions, language, method, rom_base, source_sha256 | `analysis/ghidra/a6000-darwin-adc-phase-notification.json` |
| 66 | 125512 | no | dict | coverage, function_count, targets | `analysis/ghidra/a6300-caif-sio-channel-references.json` |
| 59 | 1220955 | no | dict | constant_memory_assumption, functions, method, source_sha256 | `analysis/ghidra/capture-exposure-mode-gate.json` |
| 46 | 8148353 | no | dict | base, functions, method, source_sha256 | `analysis/ghidra/s32-callback-layout.json` |
| 41 | 115363 | no | list_of_dict | args, tool | `analysis/rea-independent/exp1a.json` |
| 29 | 1020184 | no | dict | library, reused, rtti, sha256_after, sha256_before, windows | `analysis/session21/evidence/codex-dcf-publication-tail.json` |
| 29 | 505969 | no | list_of_dict | entry, pseudo_code, query, status | `analysis/session22/evidence/s29-mpr-completion.json` |
| 24 | 996713 | no | list_of_scalar | (sin claves) | `analysis/rea-independent/exp2-hist-entries.json` |
| 22 | 48709 | no | list_of_dict | start, temporary_listing | `analysis/ghidra/s42-factory-linear.json` |
| 22 | 330383 | no | dict | a6000, a6300, a7s | `analysis/s138_camera_main_fc/fc_strings.json` |
| 22 | 3395539 | SÍ | dict | callers, library, literals, outgoing, plt, references, rtti, sha256, symbols, virtuals, window_owners, windows | `analysis/session20/evidence/codex-dcf-actual-write.json` |
| 19 | 12468859 | SÍ | dict | data_queries, functions, pic_references, sha256, strings | `analysis/ghidra/s39-closure.json` |
| 17 | 359308 | no | dict | branch_candidates, library, reused, rtti, sha256_after, sha256_before, target_relocations, target_virtuals, windows | `analysis/session21/evidence/codex-command9-followup.json` |
| 15 | 96070 | SÍ | list_of_dict | address, value | `analysis/s500_vdf/vdf_strings.json` |
| 13 | 790 | no | dict | counts | `analysis/s502_eis/eis_compare.json` |
| 12 | 266444 | no | dict | functions, method, source_sha256 | `analysis/ghidra/silent-alias-proof.json` |
| 12 | 2345118 | no | dict | artifacts, captures, environments, providers, records, scenarios, unknowns | `analysis/rea/CautionConfig-evidence.json` |
| 12 | 6141378 | no | dict | binding, entries, evidence_bundle, target, workflow_entries | `analysis/rea/CautionConfig.snapshot.json` |
| 12 | 36100 | SÍ | list_of_dict | address, name, ref_count | `analysis/s502_eis/eis_functions.json` |
| 11 | 23 | no | empty_list | (sin claves) | `analysis/ghidra/s42-pic.json` |
| 10 | 86363 | no | dict | runs, session | `analysis/session19/codex-runs/run-001/orchestration/codex-continuous-ledger.json` |
| 10 | 65241 | no | list_of_dict | effort_requested, errors, files_created, files_modified, finish_reason, model_requested, next_task_available, next_task_id, run_number, status, task_id | `analysis/session19/codex-runs/run-001/orchestration/progress.json` |
| 9 | 17646 | no | dict | functions, language, method, source_sha256 | `analysis/ghidra/a6000-darwin-shutter-adc-inventory.json` |
| 9 | 58170 | no | dict | functions, image_bias, limitation, method, source_sha256 | `analysis/ghidra/a6300-shared-queue-producers.json` |
| 9 | 180431 | no | dict | count, module, strings | `analysis/s113_cam_dmm/strings_raw.json` |
| 8 | 45637 | no | dict | A6000_fw321, A6300_fw201, A7S_fw320 | `analysis/s109_cdiag/cdiag_class_table.json` |
| 7 | 15623 | no | dict | cases, entry, limitation, method, passed, source_sha256 | `analysis/ghidra/a6000-mode-emulation-verified.json` |
| 7 | 199036 | no | dict | functions, module | `analysis/s113_cam_dmm/func_map.json` |
| 6 | 3800 | no | dict | calls | `analysis/rea-independent/jpeg_query.json` |
| 6 | 34380 | no | dict | A6000, A6300, A7S | `analysis/s177_cam_func_mgr/cfm_reqreply_tables.json` |
| 6 | 144275 | no | dict | A6000, A7S | `analysis/s55/events_mmio.json` |
| 6 | 23489 | no | dict | differential, global_logger, level_prefix, logger_dual, module, parent_prefix, prefix, prefix_length, shutter_line, sub_prefix, trace_strings, traces … | `analysis/s610_housing/housing.json` |
| 5 | 35418 | no | dict | analysis_profile, authority, confidence, environment, evidence_id, evidence_links, limitations, locations, normalized_result, operation, parameters, predicate_type … | `analysis/functions/rea-takePicture-decompile.json` |
| 5 | 6420 | no | dict | analysis/ghidra/silent-liro.gpr, analysis/ghidra/silent-liro.rep/idata/00/00000000.prp, analysis/ghidra/silent-liro.rep/idata/00/~00000000.db/db.93.gbf, analysis/ghidra/silent-liro.rep/idata/~index.bak, analysis/ghidra/silent-liro.rep/idata/~index.dat, analysis/ghidra/silent-liro.rep/project.prp, analysis/ghidra/silent-liro.rep/user/~index.dat, analysis/ghidra/silent-liro.rep/versioned/~index.bak, analysis/ghidra/silent-liro.rep/versioned/~index.dat, firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin | `analysis/ghidra/s46-integrity-after.json` |
| 4 | 4659 | no | list_of_dict | function, reference | `analysis/ghidra/s42-mode-refs.json` |
| 4 | 15855 | no | dict | differential, global_logger, logger_dual, module, parent_prefix, prefix, prefix_length, shutter_line, sub_prefix, trace_strings, traces, verification_status | `analysis/s609_dist/dist.json` |
| 3 | 1688238 | SÍ | dict | base, functions, immediates, literal_hits, sha256 | `analysis/ghidra/s38-routing.json` |
| 3 | 194966 | no | list_of_dict_variant | function, instruction | `analysis/ghidra/s43-fields.json` |
| 3 | 717 | no | dict | architecture, entry_point, format, path, provider_id | `analysis/rea-independent/exp2-open-args.json` |
| 3 | 596601 | no | dict | base, bin, func_files, modules, n_prologues, profile, size | `analysis/s125_imaging_rel/a6000_scan.json` |
| 3 | 102667 | SÍ | dict | date, entries, hypotheses, phase, sha256 | `analysis/s56-evidence-matrix.json` |
| 3 | 1030 | no | dict | exec, setexp, setmode, setread | `analysis/s59/claude/modediff_4c_4e.json` |
| 3 | 10177 | no | dict | differential, global_logger, logger_dual, module, prefix, prefix_length, shutter_line, trace_strings, traces, verification_status | `analysis/s614_zpd/zpd.json` |
| 3 | 7771 | no | dict | binary_sha256, findings, firmware, method, run_number, safety, session, task_id | `analysis/session19/codex-runs/run-002/evidence/lifecycle-connect.json` |
| 3 | 6250625 | no | dict | classes, methods_by_entry | `analysis/session20/evidence/libBizFw-rtti-vtables.json` |
| 2 | 2932 | no | dict | examples, failures, limitation, model, passed, passed_cases, source_sha256, start, stop_before, total_cases | `analysis/ghidra/a6000-darwin-capture-bit-emulation.json` |
| 2 | 2902 | no | dict | callback_pointer_occurrences, function, instruction_window_hex, limitations, method, model, phase_destinations, rom_base, source_sha256, status, table, table_hex … | `analysis/ghidra/a6000-darwin-phase-table-verified.json` |
| 2 | 30869 | no | dict | content, structuredContent | `analysis/ghidra/a6300-kikilog-acm-rea.json` |
| 2 | 1211645 | no | list_of_dict | function, instruction, references, site | `analysis/ghidra/s40-offset-all-xrefs.json` |
| 2 | 25405 | SÍ | dict | field_candidates, pointer_candidates, sha256 | `analysis/ghidra/s42-scan.json` |
| 2 | 7936 | no | list_of_dict_variant | function, site, target | `analysis/ghidra/s42-table-pic.json` |
| 2 | 17431 | no | dict | hits, note | `analysis/ghidra/s44-context-scalars.json` |
| 2 | 68026 | no | list_of_dict | nodes, start | `analysis/ghidra/s47-chain-listing.json` |
| 2 | 6664 | no | list_of_dict | kind, site, target | `analysis/ghidra/s47-direct-callers.json` |
| 2 | 5732 | no | dict | a6000, a7s | `analysis/s118_sfra/a7s_diff.json` |
| 2 | 77478 | no | dict | a6300_only, a7s, a7s_only_a6000, base, command_table, commands, counts, functions, milestone, module, source_files, strings … | `analysis/s118_sfra/sfra.json` |
| 2 | 6920 | no | dict | a6000_strings, a6300_interior_exact, a6300_interior_missing, a6300_with_prefix, a7s_interior_exact, a7s_interior_missing, a7s_with_prefix | `analysis/s127_camera_main_lc/diff.json` |
| 2 | 26801 | no | dict | counts, milestone, modulos | `analysis/s128_label_map/label_map.json` |
| 2 | 7110 | no | dict | base, firmware_sha256, milestone, rea_evidence_ids, regions, scope_limit, state_got_slot | `analysis/s159_imager_state_ref/state_spill.json` |
| 2 | 40654 | no | dict | funciones, todos_los_sitios | `analysis/s170_illumi/illumi_func_map.json` |
| 2 | 26356 | no | list_of_dict | W, dest, entre_medio, flag, ldr, pool, reg, sitio, texto | `analysis/s170_illumi/illumi_pic_verificado.json` |
| 2 | 14008 | no | list_of_dict | id, id_hex, nombre, pad, slot | `analysis/s177_cam_func_mgr/cfm_nametable_A6000.json` |
| 2 | 99366 | no | dict | absolute_pointer_literals, base, counts, firmware, gates, milestone, rea_xrefs, scope_limit, sites, targets, title, verdict | `analysis/s300_state_xref_sweep/state_xref_sweep.json` |
| 2 | 10467 | no | dict | a6000, a7s, base, firmware, limits, milestone, title, verdicts | `analysis/s345_mask_reachability/mask_reachability.json` |
| 2 | 4728 | no | dict | count, unresolved_xref_addresses | `analysis/s500_vdf/vdf_unresolved_xrefs.json` |
| 2 | 148 | no | dict | count, module, note | `analysis/s515_audpinedtr/ad_functions.json` |
| 2 | 20743 | SÍ | dict | date, entries, phase, sha256 | `analysis/s54-evidence-matrix.json` |
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
| 1 | 513 | no | dict | bad, consec, ok, skipped | `analysis/camera-dumps/sfr-scan-20261020/state.json` |
| 1 | 248757 | no | dict | archivos, cargados_sin_copia | `analysis/camera-extract/manifest.json` |
| 1 | 2669 | no | dict | config_data, extents, format_inference, scope, unit_type_mapping | `analysis/dmm-extent-sizes.json` |
| 1 | 10598 | no | dict | count, known, unit_types | `analysis/dmm-unit-types.json` |
| 1 | 6435 | no | dict | alcance, cadena, clasificacion, correcciones_sesiones_previas, evidencias, modos_record_image, sesion, veredicto | `analysis/encodestill-command-flow.json` |
| 1 | 8796 | no | dict | alcance, correccion_sesion_14, encode_still_param_8_palabras, mensaje_entrada_execute, no_hay_validacion_de, propiedad_y_vida_util, region_info_0x40, resumen, semantica_unitType, sesion, tamanos_salida, transporte_a_libmpr … | `analysis/encodestill-yc-contract.json` |
| 1 | 2185 | SÍ | list_of_dict | address_space, binary, confidence, incoming, instruction_address, original_name, outgoing, pending, sha256, symbol_value, variables | `analysis/functions/dossiers.json` |
| 1 | 1436 | SÍ | dict | accepted_message_ids, binary, binary_sha256, candidate_elf_entry, candidate_ghidra_entry, confidence, date, ghidra_string_reference_site, hardware_support, id, incoming_references, limitations … | `analysis/functions/silent-shutter-converter.json` |
| 1 | 4470 | no | dict | address_space, backend, board_defaults, date, handler, header_normalization, independent_osal_evidence, limits, registration, source_sha256, status | `analysis/ghidra/a6300-caif-sio-endpoint-checkpoint.json` |
| 1 | 9910 | no | dict | functions, method, raw_base, source_sha256 | `analysis/ghidra/a6300-imx284-readout-helpers.json` |
| 1 | 407895 | no | dict | method, program, queries | `analysis/ghidra/camera-main-sync-final-evidence.json` |
| 1 | 3928 | no | dict | date, dma_source, gpio_map, inhibit_error_mask, interrupt_dispatch, method, next, rom_base, source_sha256, status | `analysis/ghidra/darwin-dma-gpio-checkpoint.json` |
| 1 | 14132 | no | dict | a6000_source_sha256, a6300_source_sha256, emulation, evidence, inference, not_verified, scope, verified_a6000, verified_a6300, verified_efcs_packet_bridge, verified_liro_peer_handshake | `analysis/ghidra/darwin-mechanical-enable-checkpoint.json` |
| 1 | 2895 | no | list_of_dict_variant | entry, pseudo_code, status | `analysis/ghidra/dataflow-sendasync.json` |
| 1 | 173289 | SÍ | dict | functions, method, raw_ranges, sha256, singleton_writer_fragment, static_pointer_values | `analysis/ghidra/imx210-setread-config-instructions-20261018.json` |
| 1 | 1141 | no | dict | policy, queries, source_sha256 | `analysis/ghidra/rejected-queries.json` |
| 1 | 8347 | SÍ | dict | camera_connected, evidence_kind, evidence_limitations, findings, firmware, firmware_executed, logical_base, mode, original_pointer_slots, pin_objects_by_channel, primary_export, project … | `analysis/ghidra/s32-findings.json` |
| 1 | 1414 | no | dict | project_hashes, scope, source_sha256, subsequent_check | `analysis/ghidra/s32-integrity.json` |
| 1 | 8929 | no | dict | boundary_note, do_not_treat_as_function_entries, export_failures, exports, ghidra_branches_crosschecked, original_pointer_slots, overflow_strings, physical_behavior, pic_candidates, pic_scope, raw_branch_scope, raw_branches … | `analysis/ghidra/s32-raw-evidence.json` |
| 1 | 2101 | no | dict | blob_hash, camera_connected, firmware_executed, git, knowledge_graph_stability, knowledge_maintenance, knowledge_tests, mypy_touched_file, packages_installed, persistent_project, physical_capture, raw_audit … | `analysis/ghidra/s32-validation.json` |
| 1 | 10446 | no | dict | direct_calls, inputs, invalid_exploratory_entry, project_hashes, project_unchanged_against_s32_and_start_s33, result, scope, secondary_enable_source, secondary_helper_calls, source_sha256 | `analysis/ghidra/s33-audit.json` |
| 1 | 3168 | no | dict | address_prefix_table, base, findings, limits, source_sha256 | `analysis/ghidra/s33-findings.json` |
| 1 | 2702 | no | dict | direct_helper_calls, exported_queries, findings, project_unchanged, result, scope, source_sha256, unresolved_or_exploratory | `analysis/ghidra/s34-audit.json` |
| 1 | 5534 | no | dict | base, complex_interrupt, drive_event, ec_lm, exploratory_limits, helper_callers, image_runners, program_and_kick, scope, source_sha256, summary | `analysis/ghidra/s34-findings.json` |
| 1 | 1237 | no | dict | project_hashes, source_sha256 | `analysis/ghidra/s34-integrity.json` |
| 1 | 229 | no | dict | exports, project_unchanged, scan_immediates, slots_verified, source_sha256, status, vtables_verified | `analysis/ghidra/s35-audit.json` |
| 1 | 46429 | no | dict | immediate_hits, raw_hits_unaligned, source_sha256 | `analysis/ghidra/s35-causes-scan.json` |
| 1 | 2872 | no | dict | apl_access_in_resolved_activation_path, base, cause_00200000, children, conclusion, excluded_speculative_functions, ifmt_pre_helper, missing, next_exact_step, objects, operation, physical_cycle … | `analysis/ghidra/s35-findings.json` |
| 1 | 1106 | no | dict | analysis/ghidra/silent-liro.gpr, analysis/ghidra/silent-liro.rep/idata/00/00000000.prp, analysis/ghidra/silent-liro.rep/idata/00/~00000000.db/db.93.gbf, analysis/ghidra/silent-liro.rep/idata/~index.bak, analysis/ghidra/silent-liro.rep/idata/~index.dat, analysis/ghidra/silent-liro.rep/project.prp, analysis/ghidra/silent-liro.rep/user/~index.dat, analysis/ghidra/silent-liro.rep/versioned/~index.bak, analysis/ghidra/silent-liro.rep/versioned/~index.dat | `analysis/ghidra/s35-integrity.json` |
| 1 | 2094 | no | dict | address_convention, claims, next_step, project, session, source, source_sha256 | `analysis/ghidra/s36-findings.json` |
| 1 | 2535090 | no | dict | executable_sha256, functions, program | `analysis/ghidra/s36-library.json` |
| 1 | 2714 | SÍ | dict | allocation, byte_identical_s33, close_free, extent_semantics, ghidra_base, physical_yc, program, session, sha256, transport, yc_and_apl | `analysis/ghidra/s37-findings.json` |
| 1 | 1891342 | no | dict | executable_sha256, functions, image_base, program | `analysis/ghidra/s37-library.json` |
| 1 | 1644 | SÍ | dict | base, frontier, next_exact, physical_yc, receiver, sha256, summary | `analysis/ghidra/s38-findings.json` |
| 1 | 3633 | SÍ | dict | base, binary, coverage_limit, direct_consumers, enum_status, exports, input_remap_by_p_value, mapping, next_step, origin, physical_capture, session … | `analysis/ghidra/s39-findings.json` |
| 1 | 402872 | SÍ | dict | data_queries, functions, sha256, strings | `analysis/ghidra/s39-initial.json` |
| 1 | 3647 | SÍ | dict | additional_exports, alternative_selector_table, binary, context, context2, coverage, data_generation_link, dispatch_table, exports, exposure_configuration_link, flags, limitations … | `analysis/ghidra/s40-findings.json` |
| 1 | 37956 | SÍ | dict | count, dispatch, dispatch_base, selector_base, selector_raw, sha256, stride | `analysis/ghidra/s40-tables.json` |
| 1 | 1909 | SÍ | dict | binary, coverage, exports, findings, physical_capture, session, sha256, static_frontier_exhausted | `analysis/ghidra/s41-findings.json` |
| 1 | 132026 | SÍ | dict | command_instructions, constants, sha256, strings | `analysis/ghidra/s41-inventory.json` |
| 1 | 4547 | no | list_of_dict_variant | function, reference | `analysis/ghidra/s42-data-refs.json` |
| 1 | 1923 | SÍ | dict | binary, coverage, findings, line_e, physical_capture, session, sha256, static_frontier_exhausted | `analysis/ghidra/s42-findings.json` |
| 1 | 1670 | SÍ | dict | backend_offset, caller, channel_map, claims, consumer, high_nibbles, mmio_banks, mode_bytes, mode_codes, register_count, register_table, session … | `analysis/ghidra/s44-findings.json` |
| 1 | 22977 | no | list_of_dict | references, slot, target | `analysis/ghidra/s44-pointers.json` |
| 1 | 555 | SÍ | dict | c, context, context_status, controller_offset, controller_write, getter, p_to_c_copy_status, physical_integration_end_status, root_copy, series, sha256, timing_consumer … | `analysis/ghidra/s45-findings.json` |
| 1 | 250 | no | list_of_dict | reference | `analysis/ghidra/s45-object-refs.json` |
| 1 | 1507 | SÍ | dict | c_callback_slot, c_command_key, c_condition, c_dispatcher, c_payload, c_scratch, c_stores, c_table, c_table_row, c_writer, c_writer_status, next … | `analysis/ghidra/s46-findings.json` |
| 1 | 426 | no | dict | arm, caution, method, thumb | `analysis/ghidra/s47-copy-thunk-derived.json` |
| 1 | 1299 | SÍ | dict | callback_before_copy, consumed_c, copy_destination_root, copy_offset, copy_size, copy_source_root, date, dispatcher, dispatcher_payload, incoming_callback, incoming_key_offset, incoming_payload_offsets … | `analysis/ghidra/s47-findings.json` |
| 1 | 394274 | no | list_of_dict | entry, nodes | `analysis/ghidra/s47-order-flow.json` |
| 1 | 2226 | no | list_of_dict | literal, load, site, target | `analysis/ghidra/s47-raw-pic.json` |
| 1 | 6175 | no | list_of_dict | function, literal, near_listing, site, target | `analysis/ghidra/s47-request-pic.json` |
| 1 | 41410 | no | list_of_dict | function, immediate, site | `analysis/ghidra/s47-request-window.json` |
| 1 | 94096 | no | dict | external_file_count, external_matches, limitation, literal_addresses | `analysis/ghidra/s48-literals.json` |
| 1 | 7167 | SÍ | dict | ctor_stack_args, elf, modes | `analysis/imx210-drvparam-inputs.json` |
| 1 | 11119 | SÍ | dict | modes, rows | `analysis/imx210-setmode-register-matrix.json` |
| 1 | 10846 | no | dict | contradicciones, fuentes, hallazgos_nuevos_cruzados, incidente, metodo, nota_contradicciones, respuestas_informe_final, sesion | `analysis/liveview-encodestill-crosscheck.json` |
| 1 | 10261 | no | dict | bloque_0xB0, consumidor, equivalencia_12B, estado, evidencias, item_0x100E, items_0x100C_0x100D, no_verificado, nota_direcciones, productor, sentinelas_y_errores, sesion … | `analysis/objstillpool-100b-layout.json` |
| 1 | 2222 | no | dict | architecture, blocked, classification_mode4, graph, objects, session, wsi_param_layout | `analysis/objstillrecorder-mode4-flow.json` |
| 1 | 271 | no | dict | AllocDmmMemory, CtrlAllocDmmMemory, DmmAllocateNEWAndOpen_body, DmmCloseAndFree, GetExtListTop, GetExtSizeFromDmmAlloc, GetUnitHandle, SetExtListPackStatus | `analysis/rea-independent/exp1-functions.json` |
| 1 | 1613 | SÍ | list_of_dict | addr, addr_seq_equal, file_offset_ok, fn, n_objdump, n_rea, rea_bytes_eq_file, text_equal_after_norm | `analysis/rea-independent/out/exp1-bytes-check.json` |
| 1 | 5576 | SÍ | list_of_dict | addr, asm_equal, callees_rea, hist_calls, hist_name, hist_pseudo_len, hist_thunk, n_insn_hist, n_insn_rea, name, rea_calls, rea_name … | `analysis/rea-independent/out/exp1-comparison.json` |
| 1 | 98773 | SÍ | list_of_dict_variant | addr, addr_seq_equal, bytes_in_body, error, first_diff, hist_file, insn_hist, insn_in_ranges, llvm_decoded_at_addr, llvm_mnemonic_equal, n_insn, name … | `analysis/rea-independent/out/exp2-comparison.json` |
| 1 | 2373 | no | dict | 0x436c5b28, 0x436c5d20, 0x436c5d2c, 0x436c6288, 0x436c6294, 0x436c68a8, 0x436c68c4, 0x436c6f3c, 0x436c72e4, 0x436c72f4, 0x436c7490, 0x436c74c8 … | `analysis/rea-independent/out/exp2-mmio-base-users.json` |
| 1 | 1580 | no | dict | miss, notent | `analysis/rea-independent/out/exp2c-summary.json` |
| 1 | 532 | no | dict | 000012f3, 0000c3f3 | `analysis/rea-independent/out/exp2e-matches.json` |
| 1 | 3872 | no | dict | 0x436c5b3a, 0x436c5b48, 0x436c5b5c, 0x436c5b70, 0x436c5c30, 0x436c5cd0, 0x436c5cec, 0x436c5cf0, 0x436c5d04, 0x436c5d20, 0x436c5dbe, 0x436c5dea … | `analysis/rea-independent/out/exp2f-src.json` |
| 1 | 3346654 | no | dict | id, jsonrpc, result | `analysis/rea-independent/out/tools-list.json` |
| 1 | 1065 | SÍ | list_of_dict | address, procedure | `analysis/rea-independent/run/c2-investigacion.json` |
| 1 | 2241 | no | dict | blocked_pending, getfileimage_class, message_0x3a48, minimum_contract_for_mpr, new_functions, recommended_architecture, recordStillImage_0x1027, record_offsets_0x30_0x3c, session, thumbnail_screennail_producer | `analysis/record-image-completion-flow.json` |
| 1 | 1196 | no | dict | addr_note, conclusion, functions, record_offsets, session, unverified | `analysis/record-still-image-flow.json` |
| 1 | 18662 | no | dict | aristas, nodos | `analysis/s101_shutter_type/graph/module_graph.json` |
| 1 | 6268 | no | dict | code_flow, description, key_functions, module_range_a6000, module_range_a7s, msg_id_count, msg_ids, prefix, relationships, sdf_err_messages, string_prefix, string_prefix_err | `analysis/s103_sdf/sdf_module.json` |
| 1 | 28540 | no | dict | a7s, a7s_note, address_rule, base_vaddr, blob, corrections, counts, firmware, method, milestone, model, prefixes | `analysis/s104_prefixes/a6000_prefixes.json` |
| 1 | 32192 | SÍ | dict | binary, convention, counts, method, milestone, notes, strings, tables, title | `analysis/s105_panorama/keyword_inventory.json` |
| 1 | 111022 | SÍ | dict | binary, ccnr, counts, flows, key_functions, links_other_milestones, method, milestone, open_questions, strings_inventory, title | `analysis/s105_panorama/panorama_bracket_interval.json` |
| 1 | 93606 | no | dict | A6000-fw321, A6300-fw201, A7S-fw320, diff_a6000_only, diff_a7s_only | `analysis/s106_imaging_cap/imaging_cap_a7s_diff.json` |
| 1 | 107734 | SÍ | dict | a7s_diff, base, binary, blocks, counts, milestone, module, range, sections, source_file_groups, source_files, unreferenced_strings | `analysis/s106_imaging_cap/imaging_cap_architecture.json` |
| 1 | 94966 | no | dict | base, blocks, count, module | `analysis/s106_imaging_cap/imaging_cap_blocks.json` |
| 1 | 272522 | no | dict | 0x43c90000, 0x43c9000d, 0x43c90020, 0x43c90031, 0x43c9007c, 0x43c9008b, 0x43c9009b, 0x43c900b6, 0x43c900ec, 0x43c9013a, 0x43c90141, 0x43c90150 … | `analysis/s106_imaging_cap/pic_refs.json` |
| 1 | 24374 | no | dict | 0x43c9b335, 0x43c9b356, 0x43c9b376, 0x43c9b399, 0x43c9b3bb, 0x43c9b3da, 0x43c9e50f, 0x43c9ee77, 0x43c9ee9e, 0x43c9eece, 0x43c9ef02, 0x43c9ef3e … | `analysis/s106_imaging_cap/pic_refs_strict.json` |
| 1 | 708548 | no | dict | 0x435926f9, 0x435993d1, 0x4359a81d, 0x4359ad45, 0x4359ba05, 0x435a82c1, 0x435ac1c1, 0x435b38dd, 0x4361ccf1, 0x436293d5, 0x4363bf19, 0x4363bf2d … | `analysis/s106_imaging_cap/pic_refs_strict_global.json` |
| 1 | 34556 | no | dict | 0x43c9b335, 0x43c9b356, 0x43c9b376, 0x43c9b399, 0x43c9b3bb, 0x43c9b3da, 0x43c9e50f, 0x43c9ee77, 0x43c9ee9e, 0x43c9eece, 0x43c9ef02, 0x43c9ef3e … | `analysis/s106_imaging_cap/pic_refs_v2.json` |
| 1 | 6060 | no | list_of_dict | end, handler, section_id, size, strings | `analysis/s106_imaging_cap/section_handlers.json` |
| 1 | 8099 | no | dict | count, files, groups, range | `analysis/s106_imaging_cap/source_files.json` |
| 1 | 74638 | no | list_of_dict | off, text, vaddr | `analysis/s106_imaging_cap/strings_raw.json` |
| 1 | 12516 | no | dict | base_vaddr, count_strings, differential_a7s, firmware, library, milestone, model, no_verificado_abierto, related_libraries, resource_stack, rtti_camera7camcore13splitrdcimagee, rtti_camera7camcore8rdcimagee … | `analysis/s107_camcore/camcore_resources.json` |
| 1 | 4181 | no | dict | base_vaddr, file_size, firmware, grand_total, sub_blocks, total_by_subblock, total_strings, vaddr_range, verification | `analysis/s108_camera_sa/camera_sa.json` |
| 1 | 152196 | no | dict | base_vaddr, bin, by_class, class_names, count_cdiag_token, count_strings_starting_with_prefix, count_strings_with_ERR_prefix, differential, err_strings, firmware, function_signatures, milestone … | `analysis/s109_cdiag/cdiag.json` |
| 1 | 20204 | no | dict | comparison, models | `analysis/s109_cdiag/cdiag_diff.json` |
| 1 | 792086 | no | dict | 0x43c24000, 0x43c24010, 0x43c24012, 0x43c24024, 0x43c2402c, 0x43c2402e, 0x43c2403e, 0x43c24052, 0x43c2405e, 0x43c24070, 0x43c24670, 0x43c246b6 … | `analysis/s109_cdiag/cdiag_refs.json` |
| 1 | 128 | no | dict | comunes_a7s, solo_a6000 | `analysis/s110_camera_main_yc/a7s_diff.json` |
| 1 | 124394 | no | dict | blocks, module | `analysis/s110_camera_main_yc/blocks.json` |
| 1 | 267748 | no | dict | functions, module, n_functions, sin_funcion | `analysis/s110_camera_main_yc/func_map.json` |
| 1 | 180764 | no | dict | module, strings | `analysis/s110_camera_main_yc/functions.json` |
| 1 | 8393 | no | dict | files, module | `analysis/s110_camera_main_yc/source_files.json` |
| 1 | 112484 | no | dict | base, count, module, strings | `analysis/s110_camera_main_yc/strings_raw.json` |
| 1 | 32192 | no | dict | a7s, api_yc, blocks, counts, job_yc, milestone, module, submodules | `analysis/s110_camera_main_yc/yc_summary.json` |
| 1 | 505 | no | dict | a6000, a7s, identical_multiset, identical_texts, only_a6000, only_a7s | `analysis/s111_trk/a7s_diff.json` |
| 1 | 75173 | no | dict | bin, code_hi, code_lo, module, n_functions, n_referenced, n_sites, n_sites_relaxed, n_sites_strict, n_sites_unowned, n_strings, strings | `analysis/s111_trk/refs.json` |
| 1 | 25322 | no | dict | base, bin, module, n_occurrences, n_runs, strings | `analysis/s111_trk/strings_raw.json` |
| 1 | 26884 | no | dict | a7s_diff, base_vaddr, bin, blocks, code_scan, counts, functions, milestone, module, relaxed, sources, string_range … | `analysis/s111_trk/trk.json` |
| 1 | 289865 | no | dict | a7s, base_vaddr, functions, module, n_functions, string_count, strings, subblocks, total_strings, vaddr_range | `analysis/s112_camera_main_sync/camera_main_sync.json` |
| 1 | 19303 | no | dict | a7s_only_a6000, counts, error_classes, functions, milestone, module, operations | `analysis/s113_cam_dmm/summary.json` |
| 1 | 8993 | no | dict | sections, selectors, table | `analysis/s114_sections/section_map.json` |
| 1 | 65453 | no | dict | a7s_only_a6000, counts, functions, interrupt_handlers, milestone, module, p2s_channels, submodules | `analysis/s115_cam_imager/summary.json` |
| 1 | 6300 | no | dict | 0x43ce7661, 0x43ce767f, 0x43ce78ec, 0x43ce8cde, 0x43ce8d2f, 0x43ce9407, 0x43ce9436, 0x43ce9467, 0x43ce94af, 0x43ce9511, 0x43ce955e, 0x43ce9591 … | `analysis/s116_sfrs/pic_refs_sfrs.json` |
| 1 | 42812 | no | dict | artifact, counts, differential_a7s, functions, milestone, module, ranges, source_files, sub_blocks, unverified | `analysis/s116_sfrs/sfrs.json` |
| 1 | 33633 | no | dict | a7s, counts, dec_views, functions, identities, layout, milestone, module, strings, writers | `analysis/s117_augi/augi.json` |
| 1 | 2384 | no | dict | 0x43c6a28a, 0x43c6a909, 0x43c6a944, 0x43c6a97f, 0x43c6a9ba, 0x43c6a9f5, 0x43c6aa30, 0x43c6aa6b, 0x43c6aaa6, 0x43c6aae1, 0x43c6ab1c, 0x43c6ab57 … | `analysis/s117_augi/augi_refs.json` |
| 1 | 2055 | no | dict | calls, calls_from, n_funcs | `analysis/s118_sfra/call_census.json` |
| 1 | 8674 | no | list_of_dict | consts, func, imm, name, reg, site, text, vaddr | `analysis/s118_sfra/cmd_ids.json` |
| 1 | 3751 | no | list_of_dict | cmd_id, level, line_ScalarInfraAsyncMain_cpp, msg_type, name, pred, site, text, vaddr | `analysis/s118_sfra/command_table.json` |
| 1 | 48257 | no | list_of_dict | n_cand, n_hits, nearest_dist, nearest_is_hit, other_hits, reg, sfra_hits, site | `analysis/s118_sfra/pic_audit.json` |
| 1 | 648920 | no | dict | 0x4357ad77, 0x437bd306, 0x437bd98e, 0x438aafe2, 0x438ab4bc, 0x438fa01e, 0x438fe8fe, 0x438fe9d0, 0x438fe9f6, 0x438fea02, 0x438feb7a, 0x438fec32 … | `analysis/s118_sfra/pic_refs.json` |
| 1 | 14744 | no | dict | 0x4398e399, 0x439902fd, 0x4399030d, 0x4399031d, 0x4399032d, 0x4399033d, 0x43bd4650, 0x43c400db, 0x43c48bc3, 0x43c81847, 0x43c81a55, 0x43c81e90 … | `analysis/s118_sfra/pic_refs_dataflow.json` |
| 1 | 1716 | no | list_of_dict | line, pred, text, vaddr | `analysis/s118_sfra/protocol_main.json` |
| 1 | 19778 | no | dict | 0x4398e60c, 0x4398e646, 0x4398e684, 0x4398e6a8, 0x4398e758, 0x4398e796, 0x4398e808, 0x4398e81c, 0x4398e840, 0x4398e864, 0x4398e944, 0x4398e964 … | `analysis/s118_sfra/site_best.json` |
| 1 | 44503 | SÍ | dict | api_calls, base_vaddr, callers, canon_false_positives, counts, differential, firmware, functions, milestone, module, source_files, strings … | `analysis/s119_apl/apl.json` |
| 1 | 8075 | no | dict | a7s_base, funcs, n_traces, traces | `analysis/s119_apl/apl_a7s_map.json` |
| 1 | 17146 | no | dict | module, n, traces | `analysis/s119_apl/apl_map.json` |
| 1 | 600 | no | dict | 0x43874674, 0x438765c8, 0x438765fc, 0x43876a80, 0x43876ab4, 0x43876b74, 0x43876c0c, 0x43876cc6, 0x43876d08, 0x43876ea4 | `analysis/s119_apl/callers.json` |
| 1 | 553556 | no | dict | 0x43c90000, 0x43c9000d, 0x43c90020, 0x43c90031, 0x43c9007c, 0x43c9008b, 0x43c9009b, 0x43c900b6, 0x43c900ec, 0x43c9013a, 0x43c90141, 0x43c90150 … | `analysis/s119_apl/pic_refs.json` |
| 1 | 15604 | no | dict | 0x439ee7e8 | `analysis/s120_idt_opd/block_fields.json` |
| 1 | 190283 | no | dict | bin, convencion, counts, diferencial, estructuras, functions, gemelos_idt, metodo_referencias, milestone, modelo, module, sin_referencia … | `analysis/s120_idt_opd/idt_opd.json` |
| 1 | 9567 | SÍ | list_of_dict_variant | addr, base, expr, kind, offset, reg, site, text | `analysis/s120_idt_opd/map_block_table.json` |
| 1 | 38078 | no | dict | 0x439d2dfe, 0x439d30a6, 0x439d3176, 0x439d7007, 0x439d720f, 0x439d7551, 0x439d87d1, 0x439d896d, 0x439d8b85, 0x439d8c7d, 0x439d9681, 0x439d98d9 … | `analysis/s120_idt_opd/pic_refs_idt_code.json` |
| 1 | 203962 | no | list_of_dict | callee, mod, site, text, vaddr | `analysis/s120_idt_opd/sites_by_callee.json` |
| 1 | 185518 | no | dict | a6000_only, a6300_only, a7s_only, base, bin, counts, functions, milestone, module, range, sites, submodules | `analysis/s120_idt_opd/summary.json` |
| 1 | 32285 | SÍ | dict | a6300_fw201, a7s_fw320, base, binary, counts, functions, kill_analysis, milestone, module, module_reading, not_verified, pic_rule … | `analysis/s121_aip/aip.json` |
| 1 | 6675 | no | dict | module, pairs, rule | `analysis/s121_aip/kill_refs_aip.json` |
| 1 | 114394 | SÍ | dict | base_vaddr, callers, counts, dead, differential, dispatch, emitters, firmware, functions, method, milestone, module … | `analysis/s122_camera_main_tc/camera_main_tc.json` |
| 1 | 712 | no | dict | dead | `analysis/s122_camera_main_tc/dead_check.json` |
| 1 | 47990 | no | dict | a6300_fw201, a7s_fw320 | `analysis/s122_camera_main_tc/diff_versions.json` |
| 1 | 29803 | no | dict | hits, printers | `analysis/s122_camera_main_tc/emitters.json` |
| 1 | 33754 | no | dict | hits, n, rule | `analysis/s122_camera_main_tc/refs_targeted.json` |
| 1 | 102970 | no | dict | counts, dead, functions, milestone, module, rule, strings, subblocks, subblocks_content, versions | `analysis/s122_camera_main_tc/tc_map.json` |
| 1 | 15767 | no | dict | a6000, a6300, a7s, comunes_a6300, comunes_a7s, solo_a6000, tabla | `analysis/s123_camera_main_cc/a7s_diff.json` |
| 1 | 5046 | SÍ | dict | callers, module | `analysis/s123_camera_main_cc/callers.json` |
| 1 | 95788 | SÍ | dict | a7s_diff, a7s_diff_tabla, base, callers, callgraph, capture_identity_layout, class_registry, counts, functions, milestone, module, param_ids … | `analysis/s123_camera_main_cc/camera_main_cc.json` |
| 1 | 1756 | no | dict | class_names, table, typeinfos | `analysis/s123_camera_main_cc/class_registry.json` |
| 1 | 20799 | SÍ | dict | functions, module, n_functions, n_sites, rule, xrefs | `analysis/s123_camera_main_cc/func_map.json` |
| 1 | 2432 | no | dict | module, movw | `analysis/s123_camera_main_cc/param_ids.json` |
| 1 | 341549 | no | dict | cc_regions, files, module | `analysis/s123_camera_main_cc/source_files.json` |
| 1 | 5294 | no | dict | module, stages | `analysis/s123_camera_main_cc/stage_states.json` |
| 1 | 5793 | no | dict | A6000, A7S, compare | `analysis/s124_exposure_params/result.json` |
| 1 | 771206 | no | dict | 0x435926f9, 0x435993d1, 0x4359a81d, 0x4359ad45, 0x4359ba05, 0x435a82c1, 0x435ac1c1, 0x435b38dd, 0x4361ccf1, 0x436293d5, 0x4363bf19, 0x4363bf2d … | `analysis/s125_imaging_rel/a6000_pic_refs.json` |
| 1 | 872132 | no | dict | 0x4355a7bd, 0x4355abd1, 0x4358d2ed, 0x43592fd5, 0x43593c95, 0x4359ec25, 0x435aaf81, 0x43631869, 0x43636521, 0x43649089, 0x4365e471, 0x4365e485 … | `analysis/s125_imaging_rel/a6300_pic_refs.json` |
| 1 | 736930 | no | dict | 0x435600a9, 0x435604bd, 0x43591055, 0x43596bed, 0x435978ad, 0x435a283d, 0x435ab6b9, 0x4361bce9, 0x4361f255, 0x4362d6c1, 0x436417bd, 0x436417d1 … | `analysis/s125_imaging_rel/a7s_pic_refs.json` |
| 1 | 2612 | no | dict | 0x43549020, 0x43780eb4, 0x43781424, 0x43792a0c, 0x4379d114, 0x4379d37a, 0x4379d3f8, 0x4379d83a, 0x4379e354, 0x4379e500, 0x437e643a, 0x437e6b3c … | `analysis/s125_imaging_rel/bl_callers.json` |
| 1 | 41847 | no | dict | base, modules | `analysis/s125_imaging_rel/diff.json` |
| 1 | 161663 | no | dict | base, binario, diferencial, hito, metodo, modulos, perfil, titulo | `analysis/s125_imaging_rel/imaging_rel.json` |
| 1 | 37546 | no | dict | counts, diff, functions, milestone, module, range, source_files, submodules | `analysis/s126_camera_main/summary.json` |
| 1 | 39247 | SÍ | dict | binary, counts, details, differential, functions, hit, links_s126, main_agent_review, namespace, other_strings, sources, strings … | `analysis/s127_camera_main_lc/camera_main_lc.json` |
| 1 | 7142 | no | list_of_dict | text, vaddr | `analysis/s127_camera_main_lc/strings_raw.json` |
| 1 | 11410 | no | list_of_dict | func, sites, text, vaddr | `analysis/s127_camera_main_lc/strings_sites.json` |
| 1 | 17451 | SÍ | dict | base_vaddr, binary, counts, diff, dispatch, firmware, functions, method, milestone, module, relation_s115, relation_s124 … | `analysis/s129_camera_main_im/camera_main_im.json` |
| 1 | 5777 | no | dict | funcs_target, n_funcs_prologue, n_funcs_target, n_sites, sites | `analysis/s129_camera_main_im/entries_cmp.json` |
| 1 | 8987 | no | list_of_dict | bl, func, n_sites, sites, strings | `analysis/s129_camera_main_im/func_map.json` |
| 1 | 5797 | no | list_of_dict | off, sites, text, vaddr | `analysis/s129_camera_main_im/strings_raw.json` |
| 1 | 27063 | no | dict | cadenas, counts, diff, familias, ficheros_fuente, funciones, milestone, module, rango | `analysis/s131_vph_api/vph_api.json` |
| 1 | 5926 | no | dict | ClkChgExec, DelayChgExec, close_subsystem, ddl_clkctrl_close_clk, ddl_clkctrl_close_dly, ddl_clkctrl_get_clk_chg_enable, ddl_clkctrl_lock_sync_signal, ddl_clkctrl_open_clk, ddl_clkctrl_open_dly, ddl_clkctrl_set_sync_initial_signal, ddl_clkctrl_set_sync_signal, ddl_clkctrl_set_sysv_delay … | `analysis/s132_clk_ctrl/callers.json` |
| 1 | 36975 | no | dict | api_ddl_despachador, api_ddl_mapa, base, bin, cadenas, consumidores, conteo, conteo_subbloques, diferencial, funciones, milestone, modulo … | `analysis/s132_clk_ctrl/clk_ctrl.json` |
| 1 | 81325 | SÍ | dict | binary, counts, details, differential, functions, hit, main_agent_review, namespace, other_strings, sinks, sources, strings … | `analysis/s133_mount_debug/mount_debug.json` |
| 1 | 60397 | SÍ | dict | binary, counts, functions, milestone, strings, vaddr_rule, xref_rule | `analysis/s133_mount_debug/mount_debug_raw.json` |
| 1 | 6416 | no | dict | accesor_estado, global_estado, udiv, validador | `analysis/s134_imager_params/disasm.json` |
| 1 | 12594 | no | dict | base, counts, hits, milestone | `analysis/s135_elec_shutter/elec_shutter_scan.json` |
| 1 | 56739 | SÍ | dict | accessory_types, binary, classes_rtti, code_range, counters, differential, external_callers, functions, model, module, remote_keys, rtti_vtables … | `analysis/s136_accy/accy.json` |
| 1 | 17105 | no | dict | into, out | `analysis/s136_accy/accy_calls.json` |
| 1 | 29156 | no | list_of_dict | a6300_core, a6300_frag, a6300_full, a7s_core, a7s_frag, a7s_full, core, full, vaddr | `analysis/s136_accy/accy_diff.json` |
| 1 | 7718 | no | dict | 0x43562a08, 0x43562db0, 0x43562e22, 0x43562e54, 0x43562ea4, 0x43562f34, 0x43562f90, 0x43563004, 0x435630ac, 0x43563138, 0x43563174, 0x435631d2 … | `analysis/s136_accy/accy_funcs.json` |
| 1 | 18007 | no | list_of_dict | line, site, str, text | `analysis/s136_accy/accy_lines.json` |
| 1 | 32306 | no | dict | by_func, n_functions, n_referenced, n_sites, n_strings, prefix, range, strings | `analysis/s136_accy/accy_raw.json` |
| 1 | 34064 | no | dict | base_vaddr, bin, cadenas, cifras, despachadores, diferencial, ficheros_fuente, firmware, funciones, grafo_entrante, linea_obturador, modulos … | `analysis/s137_ctrlcore/ctrlcore.json` |
| 1 | 23940 | no | dict | cadenas, diferencial, ficheros_fuente, funciones, llamadores_extra, ocurrencias, punteros_4B_a_cadenas, rtti, sitios, token, totales, variantes_nombre | `analysis/s137_ctrlcore/ctrlcore_raw.json` |
| 1 | 13389 | no | dict | api_exportada, base_vaddr, convention, counters, diferencial, firmware, funciones, hito, impresor, modulo, no_verificado, rango_cadenas … | `analysis/s138_camera_main_fc/camera_main_fc.json` |
| 1 | 21 | no | dict | 0x43808000 | `analysis/s138_camera_main_fc/fc_branches.json` |
| 1 | 274 | no | dict | 0x437b7200, 0x437b7598, 0x437b777c, 0x437b7810, 0x437b7844, 0x437b7c8c, 0x437b7d6c, 0x437b7ea2, 0x437b81f0 | `analysis/s138_camera_main_fc/fc_callers.json` |
| 1 | 2385 | no | list_of_dict | a6000_other_prefix, core, core_a6300, core_a7s, full_a6300, full_a7s, text, vaddr | `analysis/s138_camera_main_fc/fc_diff.json` |
| 1 | 173 | no | dict | 0x437b7200, 0x437b74a4, 0x437b7598, 0x437b777c, 0x437b7844, 0x437b7c8c, 0x437b7d6c, 0x437b7ea2, 0x437b81f0 | `analysis/s138_camera_main_fc/fc_pic_pointers.json` |
| 1 | 1285 | no | dict | 0x43ca6944, 0x43ca6980, 0x43ca69af, 0x43ca69dc, 0x43ca6a0a, 0x43ca6a3c, 0x43ca6a66, 0x43ca6aa2, 0x43ca6aec | `analysis/s138_camera_main_fc/fc_pic_refs.json` |
| 1 | 1069 | no | dict | 0x437b7158, 0x437b7200, 0x437b74a4, 0x437b7598, 0x437b7778, 0x437b7844, 0x437b7c8c, 0x437b7d6c, 0x437b7ea0, 0x437b81f0 | `analysis/s138_camera_main_fc/fc_refs_all.json` |
| 1 | 2434 | no | list_of_dict | dest, expected, ldr, ok, site, text | `analysis/s138_camera_main_fc/fc_sites_verified.json` |
| 1 | 7776 | no | list_of_dict | name, vaddr | `analysis/s138_camera_main_fc/fc_source_files.json` |
| 1 | 1930 | no | dict | 0x437b617c, 0x437b62ac, 0x437b62c4, 0x437b6310, 0x437b633e, 0x437b644e, 0x437b6614, 0x437b6630, 0x437b6660, 0x437b66e0, 0x437b679e, 0x437b6d50 … | `analysis/s138_camera_main_fc/fc_zone_in.json` |
| 1 | 60195 | no | dict | cadenas, clase, diferencial, estados, ficheros_fuente, firmware, funciones, hito, id_modulo_log, numeros_de_linea_fuente, regla_pic, rtti_clases … | `analysis/s139_encseqctrl/encseqctrl.json` |
| 1 | 35012 | no | dict | cadenas, diferencial, ficheros_fuente, funciones, ocurrencias, punteros_4B_a_cadenas, rtti_clases, sitios, sub_bloques, token, totales | `analysis/s139_encseqctrl/encseqctrl_raw.json` |
| 1 | 25235 | SÍ | dict | banks, base_address, file_offset_rule, firmware, interpretation, milestone, pointer_table, sha256 | `analysis/s140_imager_regmap/imager_regmap.json` |
| 1 | 7193 | no | dict | base, firmware_sha256, milestone, regions, scope_limit | `analysis/s141_imager_row_trace/row_trace.json` |
| 1 | 2045 | no | dict | base, direct_xref_semantics, firmware_sha256, milestone, regions, scope_limit | `analysis/s142_imager_s_init/s_accesses.json` |
| 1 | 37710 | no | dict | ayudantes, cadenas, cadenas_sens_por_firmware, contadores, convencion, diferencial, firmware, funciones, milestone, modulo, regla_pic, tabla_despacho … | `analysis/s143_cam_util_adj/cam_util_adj.json` |
| 1 | 49416 | no | dict | ayudantes, banda_codigo, cadenas, cadenas_referenciadas_en_banda, cadenas_sens_por_firmware, contadores, convencion, diferencial, ficheros_fuente_referenciados_en_banda, firmware, funciones, globales_banda … | `analysis/s144_cam_util_sens/cam_util_sens.json` |
| 1 | 6733 | no | dict | base, firmware_sha256, milestone, rea_findings, regions | `analysis/s145_imager_unanalyzed_code/code_gap.json` |
| 1 | 1765 | no | dict | address_mappings, base, conclusion, evidence_ids, firmware_sha256, milestone, rea_tool_result | `analysis/s146_rea_seed_capability/rea_seed_capability.json` |
| 1 | 10314 | no | dict | base, coverage_limit, firmware_sha256, milestone, rea_evidence_ids, regions, row_layout_observed | `analysis/s147_imager_g_rows/g_rows.json` |
| 1 | 12852 | no | dict | base, cadenas, consumidores_verificados, contadores, datos_verificados, diferencial, funcs_emisoras, funcs_roles, fw, hito, linea_obturador, modulo … | `analysis/s148_depth/depth.json` |
| 1 | 8455 | no | dict | base, firmware_sha256, loop, milestone, rea_evidence_ids, regions, scope_limit | `analysis/s149_imager_row_helpers/row_helper_stores.json` |
| 1 | 3130 | no | dict | base, conclusion_scope, firmware_sha256, gaps, milestone, rea, tables_with_pointer_literal | `analysis/s150_imager_row_gaps/gap_refs.json` |
| 1 | 9895 | SÍ | dict | base, base_textual_panda, cadenas, callers, canales, diferencial, equivalencias_otros_firmwares, funcion_de_cadena, funciones_emisoras, helper_reporter, hito, ids_osal … | `analysis/s151_panda/panda.json` |
| 1 | 2216 | no | dict | base, descriptor_schema_observed_by_bytes, evidence_ids, firmware_sha256, matching_entries, milestone, rea, scope_limit | `analysis/s152_imager_descriptor_reads/descriptor_reads.json` |
| 1 | 2965 | no | dict | base, firmware_sha256, gate_bytes, milestone, rea_xrefs, scope_limit | `analysis/s153_imager_dump_gates/dump_gates.json` |
| 1 | 12769 | no | dict | base, firmware_sha256, milestone, procedure_ranges, rea_evidence_ids, scope_limit, slot | `analysis/s154_imager_state_ref/state_ref.json` |
| 1 | 7058 | no | dict | base, firmware_sha256, milestone, procedure_ranges, rea_evidence_ids, scope_limit, slot_values | `analysis/s155_imager_state_readers/state_readers.json` |
| 1 | 12698 | no | dict | base_vaddr, binario, cadenas, codigo_del_modulo, colas_osal_gid, contadores, diferencial, familia_loggers_s151, hito, mapa_funcion_traza, modulo, regla_referencias | `analysis/s156_tp_r/tp_r.json` |
| 1 | 6171 | no | dict | base, firmware_sha256, got_slots, milestone, procedures, rea_evidence_ids, scope_limit | `analysis/s157_imager_state_snapshot/snapshot_ref.json` |
| 1 | 6637 | no | dict | base, firmware_sha256, got_slot, milestone, procedure_ranges, rea_evidence_ids, scope_limit | `analysis/s158_imager_state_ref/state_accessor.json` |
| 1 | 9061 | no | dict | alcance, escritor_tabla_1025, escritores_modo1, escritores_reset_modo1_a_0, hallazgo_principal, limitaciones, metodo, respuesta_a_la_tarea_A1, sesion | `analysis/s16-claude-effect-mode1.json` |
| 1 | 10002 | no | dict | A2_1_modelos_que_crean_fila_0x2a, A2_2_construccion_dinamica_de_listas, A2_3_combinacion_0x0a_0x07_0x2a_en_misma_secuencia, A2_4_transiciones_hacia_modelos_de_grabacion, A2_5_otros_usos_de_stsid_6, A2_6_conexiones_temporales_crear_destruir_misma_secuencia, A2_7_otras_creaciones_de_0x2a_fuera_de_pbcap_edicion, alcance, cobertura_real, discrepancia_conteo, ids_literales_encontrados_create, ids_literales_encontrados_destroy … | `analysis/s16-claude-topology-audit.json` |
| 1 | 4645 | no | dict | addressing, binaries, camera_yc, commands, encode_still, ownership, pbcap, scope | `analysis/s16-codex-camera-yc.json` |
| 1 | 13542 | no | dict | contradicciones, fuentes, hallazgos_nuevos_cruzados, metodo, nota_contradicciones, respuestas_informe_final, sesion, verificacion_cruzada_critica | `analysis/s16-liveview-recorder-crosscheck.json` |
| 1 | 1117 | no | dict | base, firmware_sha256, milestone, rea_evidence_ids, scope_limit, state_slot, store | `analysis/s160_state_open_flag_writer/open_flag_store.json` |
| 1 | 4518 | no | dict | base, conclusion_scope, firmware_sha256, milestone, other_destination_slots, rea_evidence_ids, regions, state_pointer_slot | `analysis/s162_imager_state_event_readers/event_readers.json` |
| 1 | 10958 | no | dict | base, defaults_observed_in_decompilation, fields_read, firmware_sha256, milestone, rea_evidence_ids, regions, scope_limit, state_pointer_slots, write_destinations_not_state | `analysis/s163_imager_state_event_reader/state_event_reader.json` |
| 1 | 30785 | SÍ | dict | binary, contadores_por_subcapa, contadores_por_subcapa_sitios, counts, diferencial, diferencial_nota, functions, milestone, modulo, strings, subcapas, vaddr_rule … | `analysis/s164_camera_is/camera_is.json` |
| 1 | 10099 | SÍ | dict | binary, convention, counters, differential, functions, keycode_table, milestone, rtti, strings, subject | `analysis/s165_jog/jog.json` |
| 1 | 855 | no | dict | 0x435ae630, 0x435aea24, 0x435aea70, 0x435af848, 0x435af9b8, 0x43a4a3ba, 0x43a4a3fc | `analysis/s165_jog/jog_callers.json` |
| 1 | 8580 | no | dict | candidates, sites | `analysis/s165_jog/jog_func_sites.json` |
| 1 | 2743 | no | dict | bl, pop, push | `analysis/s165_jog/jog_funcbounds.json` |
| 1 | 32406 | no | list_of_dict | add, dest, func, is_jog, ldr, text | `analysis/s165_jog/jog_pic_sites.json` |
| 1 | 22707 | SÍ | dict | binary, clientes_liro_adc, counts, despachador_subcomandos, diferencial, diferencial_nota, estructura, ficheros_fuente, functions, milestone, modulo, pares_pic … | `analysis/s166_adc_debug/adc_debug.json` |
| 1 | 25695 | no | dict | abierto_no_verificado, cadenas, comando_entrante, diferencial, diferencial_estructural, ficheros_fuente, interes_para_la_linea_del_obturador, mapa_funcion_traza, milestone, n_cadenas_con_contenido, n_cadenas_sin_referencia, n_cadenas_solo_prefijo … | `analysis/s167_sad/sad.json` |
| 1 | 11419 | no | list_of_dict | destino_cadena, destino_calculado, ldr, literal, pool, reescrituras, reg, sitio, verificado | `analysis/s167_sad/sad_pic_verificado.json` |
| 1 | 18559 | no | dict | detalle, milestone, n_fallo, n_ok, n_sitios_verificados, regla | `analysis/s167_sad/sad_pic_verified.json` |
| 1 | 29286 | no | dict | cadenas, cotejo_mapa_global, diferencial, expansiones_sigla, funciones, milestone, n_cadenas, pic_detalle, punteros_4B_a_cadenas, sitios_por_cadena, token, totales | `analysis/s167_sad/sad_raw.json` |
| 1 | 4154 | no | dict | a6000_fw321, a6000_fw321_count_token, a6300_fw201, a6300_fw201_count_token, a7s_fw320, a7s_fw320_count_token | `analysis/s167_sad/sad_strings_raw.json` |
| 1 | 1146 | no | dict | banda, base, blob, cadenas | `analysis/s168_a6300_rolling/alive_map.json` |
| 1 | 3909 | no | dict | base_vaddr, conclusiones, efecto_en_S51, firmwares, funcion_viva, mapa_vivo_muerto_banda, milestone, refs_metodo_inverso_A6300, refs_pic_estricta_A6300, titulo | `analysis/s168_a6300_rolling/rolling.json` |
| 1 | 105994 | no | dict | n, pares | `analysis/s169_drive_api/checkset_pairs.json` |
| 1 | 23063 | no | dict | base_vaddr, capas_liro_seq, conclusiones, efecto_en_S51, firmwares, mapas_pic, milestone, propiedades_de_obturador, salvedad, titulo | `analysis/s169_drive_api/drive_api.json` |
| 1 | 801980 | no | dict | 0x4355a7bd, 0x4355abd1, 0x4358d2ed, 0x43592fd5, 0x43593c95, 0x4359ec25, 0x435aaf81, 0x435af641, 0x43631869, 0x43636521, 0x43649089, 0x4365e471 … | `analysis/s169_drive_api/pic_refs_strict_a6300.json` |
| 1 | 676814 | no | dict | 0x435600a9, 0x435604bd, 0x43591055, 0x43596bed, 0x435978ad, 0x435a283d, 0x435ab6b9, 0x435ae9a1, 0x4361bce9, 0x4361f255, 0x4362d6c1, 0x436417bd … | `analysis/s169_drive_api/pic_refs_strict_a7s.json` |
| 1 | 15880 | no | dict | agente, alcance, clasificacion_global, correccion_metodologica, dato_para_codex_c, decompilados, evidencia_cruda, hallazgo_central, proceso, respuestas_10_preguntas, sesion, siguiente_bloqueo | `analysis/s17-claude-a-topology.json` |
| 1 | 11971 | no | dict | agent, findings, local_evidence_files, message_for_principal_claude, mission, process_confirmation, session, sources_fetched_real | `analysis/s17-claude-b-api-native-flow.json` |
| 1 | 3005 | no | dict | addressing, camera, geometry, memory_contract, playdata, scope, sdf, sequence_6013, verdict | `analysis/s17-codex-c-yc-contract.json` |
| 1 | 2229 | SÍ | dict | binaries, callback, completion_to_dcf, encodestill, external_context, memory, scope | `analysis/s17-codex-d-fea-callback.json` |
| 1 | 12993 | no | dict | alcance, configuracion_real, contradicciones, fuentes, hallazgos_nuevos_cruzados, metodo, nota_contradicciones, respuestas_informe_final, sesion, verificacion_cruzada_critica | `analysis/s17-parallel-crosscheck.json` |
| 1 | 31089 | no | dict | cadenas, cifras, constantes, diferencial, diferencial_cadenas_Illumi, funciones, hito, imagen, modulo, pretty_function, rtti, rtti_diferencial | `analysis/s170_illumi/illumi.json` |
| 1 | 9721 | no | list_of_dict | n_sitios_global, n_sitios_local, sitios_global, sitios_local, solo_global, solo_local, string_addr, texto | `analysis/s170_illumi/illumi_pic_sites.json` |
| 1 | 29054 | no | list_of_dict | cadena_addr, func_end_guess, func_start, sitio, texto | `analysis/s170_illumi/illumi_region_strings.json` |
| 1 | 2 | no | empty_dict | (sin claves) | `analysis/s170_illumi/illumi_rtti.json` |
| 1 | 1855 | no | dict | IllumiAd, IllumiCam, IllumiDev, IllumiRPR0400, _ids_0x10600xx | `analysis/s170_illumi/illumi_vtables.json` |
| 1 | 6131 | no | dict | api_imager_comunes, api_imager_solo_a6300, base_vaddr, canal_steadyshot_info, conclusiones, efecto_en_S51, firmwares, get_imager_stabilization_time, milestone, nota_3_nombres_extra, propiedades_steadyshot_liro_seq, salvedad … | `analysis/s171_imager_api/imager_api.json` |
| 1 | 5587 | no | dict | base_vaddr, cadenas_de_file_y_sitios, conclusiones, correccion_a_s135, efecto_en_S51, firmwares, funcion_modo_obturador, milestone, nota_ec_assert, salvedad, tabla_no_linear, titulo | `analysis/s172_elec_shutter_a6300/elec_shutter_a6300.json` |
| 1 | 5008 | no | dict | base_vaddr, cadenas, conclusiones, detalle, efecto_en_S51, firmwares, milestone, recuentos, salvedad, titulo | `analysis/s173_cam_util_labels/cam_util_labels.json` |
| 1 | 48257 | no | dict | capa, conclusiones, efecto_en_S51, familia_del_obturador, firmwares, milestone, regla_metodologica, salvedad, solo_en_a6000, solo_en_a6300, solo_en_a7s_vs_a6000, soportados_por_a6300 … | `analysis/s174_forliro_api/forliro_api.json` |
| 1 | 4788 | no | dict | base_vaddr, cadenas, conclusiones, efecto_en_S51, firmwares, funciones, logger, milestone, recuentos, salvedad, titulo | `analysis/s175_lif_debug/lif_debug.json` |
| 1 | 2388 | no | dict | first_reader_default, got_base, got_slot, method, physical_semantics, single_read, source_sha256, state, zero_overrides | `analysis/s176_imager_state_readers/readers.json` |
| 1 | 97821 | no | dict | base_vaddr, cadenas, clases_rtti, contadores, diferencial_nucleos, doble_instrumentacion, equivalentes_otras_fw, ficheros_fuente, firmwares, funciones, hito, lrb_type_ids … | `analysis/s177_cam_func_mgr/cam_func_mgr.json` |
| 1 | 17126 | no | dict | filas, marcadores, nucleos_encontrados | `analysis/s177_cam_func_mgr/cfm_diff.json` |
| 1 | 19240 | no | dict | n_dual, sitios, wrappers | `analysis/s177_cam_func_mgr/cfm_dual_log.json` |
| 1 | 8455 | no | list_of_dict | cadenas, ficheros_y_rtti, func, n_sitios, sitios | `analysis/s177_cam_func_mgr/cfm_func_files.json` |
| 1 | 11119 | no | dict | base, entradas, stride | `analysis/s177_cam_func_mgr/cfm_functable.json` |
| 1 | 37500 | no | dict | 43 cadenas [CAM_FUNC_MGR], bloque del módulo 0x43ca1242..0x43cb0400, tabla de funciones (65) | `analysis/s177_cam_func_mgr/cfm_negativo.json` |
| 1 | 8144 | no | dict | cadenas, muertas, n_cadenas, n_funciones, n_muertas, n_sitios_total | `analysis/s177_cam_func_mgr/cfm_pic_sites.json` |
| 1 | 22425 | no | dict | filas, n_cadenas, n_gemelo_mas16, prefijo_bytes | `analysis/s177_cam_func_mgr/cfm_prefijo.json` |
| 1 | 51741 | no | dict | auditoria_pendientes, base_vaddr, conclusiones, cubiertas_como_sub_etiqueta, decodificadas, efecto_en_S51, elimina_el_a6300, metodo, milestone, nota_recuentos, pendientes_ordenadas, pendientes_reales_ordenadas … | `analysis/s178_census/census.json` |
| 1 | 76808 | no | dict | [ABB], [ACCY], [ADC_DEBUG], [ADF], [ADJ], [ADR], [AFNR], [AG], [AIP], [AMSENS], [ANNOUNCE], [APL0] … | `analysis/s178_census/census_detalle.json` |
| 1 | 7610 | no | dict | [D0], [D1], [D2], [D3], [D4], [D5], [D6], [D7], [DECMODEMGR], [EXL], [HW], [IMAGING_IMG] … | `analysis/s178_census/decisiones_auditoria.json` |
| 1 | 1625 | no | list_of_dict | add, add_bytes, cadena, ldr, ldr_bytes, pool, pool_word | `analysis/s178_census/evidencia_bytes.json` |
| 1 | 10786 | no | list_of_dict | add_vaddr, base_a_sumar_a_offsets_llvm, command, stdout | `analysis/s178_census/llvm_instrucciones.json` |
| 1 | 526414 | no | dict | antes, base_vaddr, despues, etiquetas, fuentes_sha256, limites, veredictos | `analysis/s178_census/pendientes_auditados.json` |
| 1 | 1351 | no | dict | baseline_detalle_sha256, baseline_git, consulta, error_observado, fecha_local, limite, open_binary, respaldo, resultado | `analysis/s178_census/rea_intento.json` |
| 1 | 8928 | no | list_of_dict | abs_A6000_gemelo, abs_A6000_nuevo, abs_A6300_gemelo, abs_A6300_nuevo, abs_A7S_gemelo, abs_A7S_nuevo, gemelo, texto, vaddr | `analysis/s179_cam_scalar/abs_ptrs.json` |
| 1 | 4353 | no | dict | 0x4380a688, 0x4380afec, 0x4380b1a8, 0x4380b500, 0x4380b6bc, 0x4380b8d4, 0x4380b9c4, 0x4380bb30, 0x4380bbd8, 0x4380bdbc, 0x4380c180, 0x4380c344 … | `analysis/s179_cam_scalar/calls.json` |
| 1 | 53747 | no | dict | base_vaddr, cadenas, cifras, diferencial, funciones, hito, metodo, negativo_linea_obturador, nombres_auxiliares, sigla, titulo, verificacion_pic | `analysis/s179_cam_scalar/cam_scalar.json` |
| 1 | 7329 | no | dict | funciones | `analysis/s179_cam_scalar/func_map.json` |
| 1 | 7558 | no | list_of_dict | flag, modulo, nivel, site, texto, vaddr | `analysis/s179_cam_scalar/levels.json` |
| 1 | 11110 | no | list_of_dict | gemelo, gemelo_texto, global_ok, n_sitios_gemelo, n_sitios_nuevo, sitios_gemelo, sitios_nuevo, texto, vaddr | `analysis/s179_cam_scalar/pic_full.json` |
| 1 | 3941 | no | dict | 0x43cb045a, 0x43cb0483, 0x43cb04ad, 0x43cb04d6, 0x43cb0515, 0x43cb0551, 0x43cb0588, 0x43cb05bc, 0x43cb05df, 0x43cb0607, 0x43cb0631, 0x43cb0661 … | `analysis/s179_cam_scalar/pic_sites.json` |
| 1 | 24049 | no | list_of_dict | info, kill, kind, ldr, ok, site, target, texto | `analysis/s179_cam_scalar/pic_verified.json` |
| 1 | 330380 | no | list_of_dict | sitios, texto, todos_sitios, vaddr | `analysis/s179_cam_scalar/region_strings.json` |
| 1 | 12096 | no | list_of_dict | gemelo_addr, gemelo_en_A6000, gemelo_en_A6300, gemelo_en_A7S, gemelo_texto, prefijo, sitios_gemelo_A6000, sitios_gemelo_A7S, sitios_nuevo, texto, vaddr | `analysis/s179_cam_scalar/twins.json` |
| 1 | 1442 | no | dict | 0x43566290, 0x435663b8, 0x435664d0, 0x43566558, 0x43566580, 0x435665f8, 0x435668b4, 0x4356692c, 0x43566998, 0x43566a54, 0x43566b2c, 0x43566b54 … | `analysis/s180_remote/calls.json` |
| 1 | 24664 | no | dict | funcs, remote_funcs | `analysis/s180_remote/func_map.json` |
| 1 | 27615 | no | list_of_dict | es_remoto, logger, nivel_txt, r0_id_modulo, r2_nivel, site, sub, text, vaddr | `analysis/s180_remote/levels_accy.json` |
| 1 | 7223 | no | list_of_dict | bl, dest, func, line, line_at, site, text | `analysis/s180_remote/log_calls.json` |
| 1 | 21003 | no | list_of_dict | bl_target, es_remoto, site, sub, text, vaddr | `analysis/s180_remote/logger_targets.json` |
| 1 | 4184 | no | dict | 0x43c249ec, 0x43c24a17, 0x43c24a52, 0x43c24a7c, 0x43c24aaa, 0x43c24ac2, 0x43c24aef, 0x43c24b09, 0x43c24b46, 0x43c24b96, 0x43c24bad, 0x43c24be9 … | `analysis/s180_remote/pic_local.json` |
| 1 | 23388 | no | dict | strings, twins | `analysis/s180_remote/pic_sites.json` |
| 1 | 8741 | no | list_of_dict | info, kill, ldr, ok, site, target, texto | `analysis/s180_remote/pic_verified.json` |
| 1 | 30807 | SÍ | dict | binary, counters, diferencial, estructura_de_datos, firmware, funciones, hito, logging, model, negativo_obturador, no_verificado, que_es … | `analysis/s180_remote/remote.json` |
| 1 | 6830 | no | dict | abs_ptrs, negativo, twins | `analysis/s180_remote/verify.json` |
| 1 | 6425 | no | dict | agent, date, imx210_registers, imx210_sha256, imx235_modes, imx235_registers, imx235_sha256, phase, subsystems | `analysis/s201_imx210_imx235_registers/compare.json` |
| 1 | 1601 | no | dict | agent, date, end_of_integration, imx210_readout_lines, imx210_readout_ms, imx210_sha256, imx210_svd_formula, imx210_time_registers, imx235_modes, imx235_sha256, imx235_silent_columns, imx235_time_registers … | `analysis/s202_imx210_imx235_timing/timing.json` |
| 1 | 494 | no | dict | caller, electronic_end_of_integration, rows, selector_store, source, source_sha256, staging, state, state_slot | `analysis/s205_imager_s0_writer/staging_contract.json` |
| 1 | 32623 | no | dict | agent, date, imx210_registers, imx210_sha256, imx235_modes, imx235_registers, imx235_sha256, phase, registros, resumen | `analysis/s206_imx210_imx235_full_table/full_table.json` |
| 1 | 1041 | no | dict | agent, conclusion, date, eoi_mechanism_status, eoi_strings_a6000_long, eoi_strings_a6000_short, eoi_strings_a7s_long, eoi_strings_a7s_short, exposure_timer_end_no_register_rewrite, imx210_sha256, imx235_dirs, imx235_has_eoi_dedicated_register … | `analysis/s207_imx235_end_of_integration/full_eoi.json` |
| 1 | 753 | no | dict | a6000_channel_table_p2s, a6000_p2s_formatter_0x81, a7s_channel_table_p2s, a7s_no_extra_byte, a7s_p2s_formatters, agent, conclusion, date, imx210_sha256, imx235_sha256, phase | `analysis/s208_p2s_transport/p2s_transport.json` |
| 1 | 27045 | no | dict | 0x4382e526, 0x43830994, 0x43834158, 0x43834188, 0x438363e6, 0x4383ac8e, 0x4383ac90, 0x4383afce, 0x4383b30e, 0x4383f0d2, 0x4383f1e0, 0x438475b8 … | `analysis/s300_state_xref_sweep/trace_candidates.json` |
| 1 | 2991 | SÍ | dict | base, binary, classified, gates_writers, got_slot, note, sha256, state_object, xrefs_total | `analysis/s300_state_xref_sweep/xrefs_classified.json` |
| 1 | 31576 | no | dict | 0x437d36be, 0x437d36c2, 0x437d648c, 0x437dc840, 0x437dc97c, 0x437e059e, 0x437e05a0, 0x437e05be, 0x437e05c0, 0x437e0744, 0x437e07ce, 0x437e09ba … | `analysis/s301_a7s_state_xref_sweep/trace_candidates.json` |
| 1 | 25459 | no | dict | base, claims, deltas, exposure_offsets, firmware, matrices, milestone, mode_list, mode_map, scope_limit, selector_a7s, title | `analysis/s302_drive_modes/compare.json` |
| 1 | 14962 | no | dict | base, caller_function, corrections, dumper, firmware, got_users, level3, milestone, rea, scope_limit, table, title | `analysis/s303_ref_tree/ref_tree.json` |
| 1 | 4101 | no | dict | base, firmware, milestone, reads_only, scope_limit, selector, timing_function, title, writers | `analysis/s307_a7s_writers/writers.json` |
| 1 | 1819 | no | dict | base, firmware, milestone, pointers_into_0x43864xxx, scope_limit, selector_site, timing_entry_direct_callers, title | `analysis/s308_silent_flow/flow.json` |
| 1 | 2219 | no | dict | base, chain, firmware, milestone, scope_limit, title | `analysis/s309_chain_presence/presence.json` |
| 1 | 2058 | no | dict | base, firmware, milestone, scope_limit, selector_result_path, thunks, title | `analysis/s310_vtable_thunk/thunk.json` |
| 1 | 1655 | no | dict | base, firmware, milestone, scope_limit, title, writers | `analysis/s311_a6000_config/config.json` |
| 1 | 2639 | no | dict | base, firmware, functions, milestone, scope_limit, site_rows, title | `analysis/s312_cluster_consumers/consumers.json` |
| 1 | 45473 | no | dict | a6000, call_site, descriptor_rows, firmware, limits, milestone, register_list, selector, title, vtable_thunks | `analysis/s314_selector_object/selector.json` |
| 1 | 21380 | SÍ | dict | a6000_presence, consumer, firmware, getter_L95, got, limits, lists, milestone, modes, title | `analysis/s315_register_lists/lists.json` |
| 1 | 10401 | SÍ | dict | a6000_presence, constructor, fields, firmware, limits, method_slots, milestone, title, vtable, wrapper | `analysis/s316_class_vtable/class.json` |
| 1 | 16455 | no | dict | a6000_entry_hits, entry, firmware, limits, milestone, spacing, tables, title, writers_obj_2b4 | `analysis/s317_mode_tables/mode_tables.json` |
| 1 | 11044 | no | dict | a6000_ctor_hits, constructor, firmware, limits, mapper, milestone, rea, table, title | `analysis/s318_ctor_mode/ctor_mode.json` |
| 1 | 53070 | no | dict | absolute_words_av_cam, ctx, firmware, limits, milestone, sibling_modules, title, verdict | `analysis/s319_ctx_boundary/ctx_boundary.json` |
| 1 | 8806 | no | dict | busy, common_insn, conclusion, extra_block, firmware, formatter, limits, milestone, plain_path, presence, retry_path, title | `analysis/s320_frame_retry/frames.json` |
| 1 | 32688 | no | dict | base, consumer_a6000, consumer_a7s, firmware, matrix_a7s, milestone, mode_columns, record_pool, register_lists, scope_limit, title, vtables | `analysis/s321_matrix_rows/matrix_rows.json` |
| 1 | 22264 | no | dict | byte_aligned_frame, existing_emulation, firmware, formatter, limits, milestone, mode_effect, rea | `analysis/s322_frame_format/frame_format.json` |
| 1 | 19471 | no | dict | base, column_census, column_claim_s204, consumer_34, firmware, milestone, mode_array, scope_limit, setter_a6000, setter_a7s, slot, title … | `analysis/s324_columns_audit/columns_audit.json` |
| 1 | 13224 | no | dict | accessor, base, call_chain, corrections, diffs_vs_mechanical, firmware, helper, map, mapping, milestone, mode_array, pairs_share_column … | `analysis/s325_position_map/position_map.json` |
| 1 | 10318 | no | dict | base, comparisons, firmware, milestone, mode_order, s204_verdict, scope_limit, t2_signature, tables, title | `analysis/s326_t2_fingerprint/t2_silent_fingerprint.json` |
| 1 | 5718 | no | dict | base, base_ctor_zero_init, caller, firmware, load_count, loads, milestone, parametric_ctor, scope_limit, store_count, stores, title … | `analysis/s327_row_index_writer/row_index_writer.json` |
| 1 | 1726 | no | dict | base, cases, firmware, milestone, scope_limit, title, verdict | `analysis/s328_second_matrix/second_matrix.json` |
| 1 | 140415 | no | dict | base, base_coherence, bases_from_pic, bias_calibration, consumer, corrections, descriptor_b, firmware, limits, matrix, matrix_pair_diffs, milestone … | `analysis/s329_mode_timing_tables/mode_timing.json` |
| 1 | 8674 | SÍ | dict | base, ctor, factory, known_caller, limits, milestone, scan_a6000, scan_a7s, title, verdict, vtable | `analysis/s330_ctor_instances/ctor_instances.json` |
| 1 | 23607 | no | dict | base, call_sites, consumer, consumer_callers, corrections, firmware, limits, milestone, pair_diffs, search, siblings, tables … | `analysis/s331_consumer_signature/consumer_signature.json` |
| 1 | 63567 | no | dict | a6000, a7s, base, comparison, firmware, limits, milestone, title, verdicts | `analysis/s332_a6000_tables/a6000_tables.json` |
| 1 | 7721 | no | dict | a6000, a7s, base, firmware, limits, milestone, title, verdicts, vocabulary | `analysis/s333_mode_vocabulary/mode_vocabulary.json` |
| 1 | 27194 | no | dict | apply, base, collapse, firmware, limits, milestone, op_select, per_code, title, verdicts | `analysis/s334_pair_dataflow/pair_dataflow.json` |
| 1 | 15226 | no | dict | a6000_layer, a7s_layer, base, firmware, limits, milestone, mmio, title, verdicts | `analysis/s335_mmio_layer/mmio_layer.json` |
| 1 | 39171 | no | dict | base, consumers, corrections, firmware, limits, milestone, reference_count, references, tables, title, verdicts | `analysis/s336_table_consumers/table_consumers.json` |
| 1 | 1832 | no | dict | base, firmware, limits, literal_references, milestone, prefix_43f9c622, table, title, verdicts | `analysis/s337_fef404_table/fef404_table.json` |
| 1 | 12882 | no | dict | base, corrections, dfe_block, firmware, limits, milestone, repo_evidence, strings, title, unknown_block, verdicts | `analysis/s338_block_identity/block_identity.json` |
| 1 | 2456 | SÍ | dict | accessors, all_sites_in_accessors, base, firmware, interface, known_neighbours, limits, literal_sites, milestone, registers, title, verdicts … | `analysis/s339_block_f292b/block_f292b.json` |
| 1 | 12476 | no | dict | base, cases, corrections, firmware, limits, milestone, per_code, sum, switch, title, verdicts | `analysis/s340_w0_selector/w0_selector.json` |
| 1 | 44207 | no | dict | a6000, a6300, a7s, base, cross_model, firmware, limits, milestone, negatives, title, verdicts | `analysis/s342_fef404_consumers/fef404_consumers.json` |
| 1 | 53124 | no | dict | base, chain, cross_model, decompress_case0, firmware, getters, handlers, limits, milestone, negatives, s340_cross_check, single_bit_writers … | `analysis/s343_row_copy_chain/row_copy_chain.json` |
| 1 | 12289 | SÍ | dict | a6000, base, callers, firmware, function, limits, milestone, per_mode_a6000, per_mode_a7s, tables, title, verdicts | `analysis/s344_selector_tables/selector_tables.json` |
| 1 | 17919 | no | dict | base, cross_model, field_meaning, firmware, lens_aberration_file, limits, milestone, models, negatives, title, verdicts | `analysis/s347_odl_field/odl_field.json` |
| 1 | 10380 | no | dict | base, cross_model, firmware, limits, milestone, models, title, verdicts | `analysis/s348_odl_callback/odl_callback.json` |
| 1 | 16605 | no | dict | backup_state, liro_api, recordstill, uipc_route | `analysis/s380_libobj_map/followup_audit.json` |
| 1 | 3529 | no | dict | checks, llvm_version, method | `analysis/s380_libobj_map/followup_llvm.json` |
| 1 | 142015 | no | dict | 0x102cbdc, 0x102cbe0, 0x102cbe4, 0x102cbe8, 0x102cbec, 0x102cbf0, 0x102cbf4, 0x102cbf8, 0x102cbfc, 0x102cc00, 0x102cc04, 0x102cc08 … | `analysis/s380_libobj_map/got_to_name.json` |
| 1 | 192209 | no | dict | exports_key, imports_key, n_exports_func, n_imports_func, plt_map, plt_map_count | `analysis/s380_libobj_map/key_symbols.json` |
| 1 | 566337 | no | dict | exports_func, got_map, imports_func, n_defined_func, n_dynsym, n_rel_plt, n_und_func, n_und_obj, plt_base, plt_map, plt_size, sections | `analysis/s380_libobj_map/map.json` |
| 1 | 5071 | no | dict | attempts, date, interpretation | `analysis/s380_libobj_map/rea_recordstill_coverage.json` |
| 1 | 130486 | no | dict | alcance, casos, fecha, revision_destinos, validacion | `analysis/s400_open_questions_triage/manual_review.json` |
| 1 | 1527195 | no | list_of_dict_variant | cita, contexto, destino, destino_cita, fuente, fuente_actual, motivo, motivo_anterior, revision_fuente, revision_manual, status_grafo, tipo … | `analysis/s400_open_questions_triage/triage.json` |
| 1 | 659 | no | dict | caller, capture_selector, constructor, diagnostic_override, limits, normal_bit_0x20_condition, normal_byte, payload, payload_store, physical_delivery, sensor_modes, source_sha256 | `analysis/s401_a7s_caif/caif_contract.json` |
| 1 | 213772 | no | list_of_dict | args, evidence, tool | `analysis/s401_a7s_caif/rea_evidence.json` |
| 1 | 11230 | SÍ | dict | batch_items, callback_lists, geometry_row, historical_functions, metrics, mismatches, protected_files, rea_byte_reads, sha256, stage_diag, tbb_destinations | `analysis/s50/codex/audit-result.json` |
| 1 | 93557 | no | dict | callback-count-copy, callback-dispatch, capture-cancel, copy-field, curtain-request, descriptor-init, error-flags, exposure-getter, exposure-selector, exposure-switch, init-table, initial-request … | `analysis/s50/codex/llvm-evidence.json` |
| 1 | 12428 | no | dict | common_a6000_a7s, common_strings, counts, exclusive_a6000_strings, exclusive_a6000_vs_a6300, exclusive_a6000_vs_a7s | `analysis/s500_vdf/vdf_compare.json` |
| 1 | 10622 | SÍ | list_of_dict | address, name, ref_count, xref_addresses | `analysis/s500_vdf/vdf_functions.json` |
| 1 | 4006 | no | dict | common_a6000_a7s, common_strings, counts, distinct_counts, exclusive_a6000_strings, exclusive_a6000_vs_a7s | `analysis/s501_stk/stk_compare.json` |
| 1 | 27 | no | dict | unresolved_count | `analysis/s503_zpd/zpd_unresolved.json` |
| 1 | 61 | SÍ | list_of_dict | address, name | `analysis/s504_stabilizer/stab_functions.json` |
| 1 | 279063 | no | dict | /home/nicolas/.claude/.credentials.json, /home/nicolas/.claude/settings.json, /home/nicolas/.claude/settings.local.json, /home/nicolas/.codex/auth.json, /home/nicolas/.codex/config.toml, /home/nicolas/Documents/a6000/.mcp.json, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/CONTEXT.md, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/ghidra/DecompAt.java, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/ghidra/EmulateDarwinCaptureBits.java, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/ghidra/EmulateImagerMode.java, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/ghidra/ExportSilentLiro.java, /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/ghidra/FindScalarUses.java … | `analysis/s51/deepseek/integrity-before.json` |
| 1 | 1838 | no | dict | api_error, api_error_status, duration_api_ms, duration_ms, fast_mode_disabled_reason, fast_mode_state, is_error, modelUsage, num_turns, permission_denials, queued_turn_count, result … | `analysis/s51/deepseek/phase1_result.json` |
| 1 | 583917 | no | list_of_dict | annotations, description, execution, icons, input_schema, meta, name, output_schema, title | `analysis/s51/deepseek/rea-schemas.json` |
| 1 | 96 | no | dict | reason, type | `analysis/s51/deepseek/stop.json` |
| 1 | 144 | no | dict | a6000, a6300, a7s, module, note | `analysis/s515_audpinedtr/ad_compare.json` |
| 1 | 2190 | no | dict | count, module, source, strings | `analysis/s515_audpinedtr/ad_strings.json` |
| 1 | 5746 | no | dict | agents, binaries, date, evidence, hypotheses, phase, questions | `analysis/s52-evidence-matrix.json` |
| 1 | 5580 | no | dict | binaries, date, evidence, hypotheses, phase, questions, rom_base, tools | `analysis/s53-evidence-matrix.json` |
| 1 | 8409 | no | list_of_dict | data, funcs, id, rec | `analysis/s56/rec_map.json` |
| 1 | 13395 | no | dict | 0x0, 0x1, 0x100, 0x101, 0x126, 0x127, 0x128, 0x12a, 0x12f, 0x142, 0x143, 0x144 … | `analysis/s57/bitops.json` |
| 1 | 19982 | SÍ | list_of_dict | after_setexp, base, mode, post, shut, ssb, ssb_cleared, wire_id1 | `analysis/s57/id1_grid.json` |
| 1 | 1156 | no | list_of_dict | T_s_if_1_256us, T_units, lines, n, real, shd, speed, spl, tv | `analysis/s58/out/a6000_timing_scenarios.json` |
| 1 | 392027 | no | dict | comparisons, gain_scenarios, matrix | `analysis/s58/out/a7s_effective_diff.json` |
| 1 | 9070 | SÍ | dict | maptab, modes, rows | `analysis/s58/out/a7s_matrix_corrected.json` |
| 1 | 472538 | SÍ | list_of_dict | args, device_seq, err, mmio, mode, msgs, nmsg, records, ret, seq, shut, snaps … | `analysis/s58/out/a7s_scenarios.json` |
| 1 | 1779 | no | dict | 0x4c_0x4e, 0xb_0x4c, 0xb_0x4e | `analysis/s59/claude/blockdiff.json` |
| 1 | 62144 | no | list_of_dict | real, same_dev, shadow_diff, synth_dev | `analysis/s59/claude/real_scenarios.json` |
| 1 | 9447 | SÍ | dict | accessor, clock_binding, constructor, consumer, copy, host_edges, publish, sha256, snapshot, state, synthetic_compatibility, vdnum | `analysis/s59/sol/probe-results.json` |
| 1 | 34371 | SÍ | dict | candidate_hits, sha256 | `analysis/s59/sol/static-candidates.json` |
| 1 | 12246 | SÍ | dict | baseline, date, entries, hypotheses, phase, sha256 | `analysis/s59-evidence-matrix.json` |
| 1 | 1082 | no | dict | 0x43ae8496, 0x43ae84a4, 0x43ae84b2, 0x43ae84c0, 0x43ae84cc, 0x43ae84da, 0x43ae84e8, 0x43ae84f6, 0x43ae8504, 0x43ae8510 | `analysis/s60/claude/accessor_callers.json` |
| 1 | 679 | no | dict | A_caller, B_callers, accessor_e20, producer_A_call, producer_A_dst_offsets, producer_B_call, producer_B_dst_offsets, producer_B_sixth_pair, producer_B_src_offsets | `analysis/s60/claude/e20_producers.json` |
| 1 | 641 | no | dict | examples, roles | `analysis/s60/claude/handle_roles.json` |
| 1 | 758 | no | dict | agc, base, changed_vs_base, shd, spl, svd | `analysis/s60/claude/msg_content.json` |
| 1 | 1761 | no | dict | 0x4355efdc, 0x4355eff8, 0x4355f014, 0x4355f030, 0x4355f04c, 0x4355f068, 0x4355f084, 0x4355f0c0, 0x4355f0dc, 0x4355f0f8, 0x4355f114, 0x4355f130 … | `analysis/s60/claude/osal_wrappers.json` |
| 1 | 5162 | no | dict | 0x4355e900, 0x4355fa34, 0x4355fb24, 0x435606b0, 0x43560ac4, 0x43572d5c, 0x43591278, 0x435913b8, 0x435918c4, 0x43598bbc, 0x435a2c18, 0x435ad15c … | `analysis/s60/claude/queue_literal_users.json` |
| 1 | 566 | SÍ | dict | callers, emit_callers, execute_ptr, execute_vtable_slot, handle_literals, sha256, trace_evt_in_imager_ctor_region | `analysis/s60/claude/trace_api.json` |
| 1 | 776 | no | dict | 0x1000, 0x1001, send_fail, unit_filtered | `analysis/s60/claude/trace_emu.json` |
| 1 | 638 | no | dict | case3_calls_0x43b00fe6, case4_calls_0x43b00d94, case9_calls_0x43b00f62, dispatcher_literal_0x3030f_near_recv, emitters_call_0x43806400, publish_dd4_calls, recv_0x43806e38_calls_dispatcher, send_literal_0x8003030f, sha, tbh_targets, writer_da0_tailcalls | `analysis/s60/claude/verify_sol.json` |
| 1 | 2499 | SÍ | dict | case10, case4, case_targets, injected_next, injected_source, input_kind, published_10_dd0, published_4_dd0, published_dd0, reachability, receiver_10, receiver_4 … | `analysis/s60/sol/probe-results.json` |
| 1 | 9436 | SÍ | dict | baseline, date, entries, gpt_cross_validation, hypotheses, phase, s51, sha256 | `analysis/s60-evidence-matrix.json` |
| 1 | 6455 | no | dict | cap_modes_handled, differential, emitting_functions, evidence, exclusivity, firmware, key_structures, limitations, module, osal_usage, session, string_count … | `analysis/s600_cam_func_mgr/cam_func_mgr.json` |
| 1 | 6324 | SÍ | dict | differential, emitting_function_addresses, evidence, exclusivity, firmware, key_themes, limitations, module, session, string_count, strings, verdict … | `analysis/s601_cam_scalar/cam_scalar.json` |
| 1 | 6513 | SÍ | dict | additional_remote_strings, differential, emitting_functions, evidence, exclusivity, firmware, limitations, module, session, state_fields, string_count, strings … | `analysis/s602_remote/remote.json` |
| 1 | 5244 | SÍ | dict | differential, emitting_functions, evidence, exclusivity, firmware, key_subsystems, limitations, module, session, string_count, strings, verdict … | `analysis/s603_camera_dsp_apl/camera_dsp_apl.json` |
| 1 | 5367 | no | dict | IMAGING_RAW, LENS_YC, differential, evidence, exclusivity, firmware, limitations, modules, session, string_counts, verdict | `analysis/s604_lens_yc_imaging_raw/lens_yc_imaging_raw.json` |
| 1 | 6250 | no | dict | dgi_jpeg_symbols, differential, global_logger, logger_dual, module, prefix, prefix_length, shutter_line, trace_strings, traces, verification_status | `analysis/s605_jpeg/jpeg.json` |
| 1 | 6227 | no | dict | differential, global_logger, logger_dual, module, prefix, prefix_length, shutter_line, trace_strings, traces, twin_prefix, twin_prefix_length, verification_status | `analysis/s606_nsx_vot/nsx_vot.json` |
| 1 | 8324 | no | dict | differential, global_logger, logger_dual, logger_paths, module, prefix, prefix_length, shutter_line, trace_strings, traces, typo, verification_status | `analysis/s607_cam_cmd/cam_cmd.json` |
| 1 | 6360 | no | dict | composite_prefix_length, core_prefix, core_prefix_length, differential, global_logger, logger_dual, module, prefix, prefix_length, shutter_line, trace_strings, traces … | `analysis/s608_mount_info/mount_info.json` |
| 1 | 524 | no | dict | block_hex, classification, p0_output, pairs, stubbed | `analysis/s61/e3_chain.json` |
| 1 | 3430 | no | dict | 0x437a6db8, 0x437a8e16, 0x437ab474, 0x4381eb6c, 0x43822eee, 0x4382c7f2 | `analysis/s61/g_writers.json` |
| 1 | 9708 | SÍ | dict | baseline, date, entries, gpt_cross_validation, hypotheses, phase, s51, sha256, tests | `analysis/s61-evidence-matrix.json` |
| 1 | 7874 | no | dict | composite_prefix_length, core_prefix, core_prefix_length, differential, global_logger, logger_dual, logger_paths, module, prefix, prefix_length, shutter_line, trace_strings … | `analysis/s611_imaging_rsrc/imaging_rsrc.json` |
| 1 | 5039 | no | dict | differential, global_logger, logger_dual, module, prefix, prefix_length, shutter_line, sub_prefixes, trace_strings, traces, verification_status | `analysis/s613_mount_warning/mount_warning.json` |
| 1 | 6487 | no | dict | differential, global_logger, logger_dual, logger_paths, module, prefix, prefix_length, shutter_line, trace_strings, traces, verification_status | `analysis/s616_lens_pdr/lens_pdr.json` |
| 1 | 2975 | no | dict | differential, module, note, prefix, prefix_length, related_module, shutter_line, trace_strings, traces, verification_status | `analysis/s618_det_dir/det_dir.json` |
| 1 | 4371 | no | dict | differential, global_logger, logger_dual, module, prefix_lengths, prefixes, shutter_line, trace_strings, traces, verification_status | `analysis/s619_senser/senser.json` |
| 1 | 6006 | SÍ | dict | baseline, date, entries, phase, s51, sha256 | `analysis/s62-evidence-matrix.json` |
| 1 | 3313 | no | dict | differential, global_logger, logger_dual, module, parent_prefix, prefix, prefix_length, shutter_line, trace_strings, traces, verification_status | `analysis/s625_adr/adr.json` |
| 1 | 2212 | no | dict | camera_lens_class, jobs, lens_barrier, milestone, odl, open_questions, scope, subtask | `analysis/s66/lens_class_and_jobs.json` |
| 1 | 9722 | no | dict | a6000_vs_a7s, bonobodsp, frame_format, fwupdate_path, handshake, method, milestone, open_questions, target, topic | `analysis/s66/lens_fwupdate_dsp.json` |
| 1 | 7850 | no | dict | a7s_comparison, blob_sha256, code_regions, firmware, lens_type_decode, lifecycle, milestone, model, open_questions, protocol, scope, source_files … | `analysis/s66/lens_power_attach.json` |
| 1 | 3516 | no | dict | a6000_functions, milestone, model_comparison, models, open_questions, other_shd_logs, per_lens_fields, scope, shd_mode_table, subtask, trace_helper | `analysis/s66/lens_shading.json` |
| 1 | 102155 | no | dict | codigo_A6000, ficheros, formato_fichero, meta, pares_ED_identico, slots_avcam | `analysis/s66/lensfile_format.json` |
| 1 | 32036 | no | dict | artifacts, blob, firmware, functions, legend, method, milestone, model, not_in_rea, open_questions, protocol, region … | `analysis/s66/mount_functions.json` |
| 1 | 11646 | no | dict | absent_strings_a6000, base, callers_verified, camera, charge_variable_names, compare_camera, compare_firmware_sha256, comparison_a6000_vs_a7s, conclusion, firmware, firmware_sha256, functions … | `analysis/s68_power/battery_power.json` |
| 1 | 10539 | SÍ | dict | a7s_comparison, base, binary, data_model, entries, frontier, hito, microphone, models_compared, noise_reduction, scope, sha256_avcam_a6000 … | `analysis/s69_audio/audio_subsystem.json` |
| 1 | 101778 | no | list_of_dict | firmware, json, module, verification_status | `analysis/s6xx_verification_results.json` |
| 1 | 16038 | no | dict | comparison_target, corrections_vs_subagent_draft, drivers, file_count, firmware, inventory_by_group, key_strings_and_addresses, subsystem, trk_detectors | `analysis/s71_frc/frc_subsystem.json` |
| 1 | 2919 | no | dict | corrections_vs_subagent_draft, differential, firmware, hito, libraries, netconf | `analysis/s72_wlan/wlan_playmem.json` |
| 1 | 2899 | no | dict | avcam_estilos, avcam_wb_block, corrections_vs_subagent_draft, hito, negativos_verificados, userland | `analysis/s77_pp/picture_profile_creative_style.json` |
| 1 | 2362 | no | dict | autoframing, corrections_vs_subagent_draft, etapas_control, hito, relacion_sa_inferencia_por_rodata | `analysis/s82_autoframing/autoframing_stages.json` |
| 1 | 2397 | no | dict | avcam, corrections_vs_subagent_draft, hito, userland | `analysis/s87_storage/storage_filesystem.json` |
| 1 | 2272 | no | dict | corrections_vs_subagent_draft, golfshot, hito, motionshot | `analysis/s88_shotmodes/golfshot_motionshot.json` |
| 1 | 4170 | no | dict | comparison_firmware, firmware, inventory, notes, subsystem, verified_against | `analysis/s90_playback/playback.json` |
| 1 | 3014 | no | dict | avcam_bin, comparison_fw321_vs_fw320, hito, userland_libs, verified_against | `analysis/s92_mediadb/media_database.json` |
| 1 | 3838 | no | dict | a7s_fw320_size, cam_apis_capabilities, category_ids, exported_classes, firmware, library, message_types, osal_primitives, size_bytes | `analysis/s94_hapi/hapi_api.json` |
| 1 | 2753 | no | dict | hallazgo, hito, mnt, otros, otros_sabin, spica, total_rutas, zonas | `analysis/s95_files/file_inventory.json` |
| 1 | 8607 | SÍ | dict | base, binary, comparison_a6s_vs_a7s, frontend, hito, models_compared, modules, scope | `analysis/s97_encsync/encoder_sync.json` |
| 1 | 1480 | no | dict | bridge_with_adf, cateid_categories, constant_comparison, cpp_classes, library, msg_id_constants, osald_gids, req_operation_types, size_bytes, verified_against | `analysis/s98_bizfw/bizfw_bridge.json` |
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
