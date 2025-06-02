// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pokemon.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PokemonModel _$PokemonModelFromJson(Map<String, dynamic> json) => PokemonModel(
      name: json['name'] as String?,
      totalEncounters: (json['encounters_total'] as num?)?.toInt(),
      startedHuntTimestamp: json['started_hunt_ts'] as num?,
      catches: (json['catches'] as List<dynamic>?)
          ?.map((e) => CatchModel.fromJson(e as Map<String, dynamic>?))
          .toList(),
    );

Map<String, dynamic> _$PokemonModelToJson(PokemonModel instance) =>
    <String, dynamic>{
      'name': instance.name,
      'encounters_total': instance.totalEncounters,
      'started_hunt_ts': instance.startedHuntTimestamp,
      'catches': instance.catches?.map((e) => e.toJson()).toList(),
    };
