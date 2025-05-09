// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pokemon.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PokemonData _$PokemonDataFromJson(Map<String, dynamic> json) => PokemonData(
      pokemon: json['pokemon'] as String?,
      encounters: (json['encounters'] as num?)?.toInt(),
      encounterMethod: json['encounter_method'] as String?,
      extraData: json['extra_data'] as Map<String, dynamic>?,
      caughtTimestamp: json['caught_timestamp'] as num?,
      startedHuntTimestamp: json['started_hunt_timestamp'] as num?,
      catches: (json['catches'] as List<dynamic>?)
          ?.map((e) => CatchModel.fromJson(e as Map<String, dynamic>?))
          .toList(),
    );

Map<String, dynamic> _$PokemonDataToJson(PokemonData instance) =>
    <String, dynamic>{
      'pokemon': instance.pokemon,
      'encounter_method': instance.encounterMethod,
      'encounters': instance.encounters,
      'extra_data': instance.extraData,
      'caught_timestamp': instance.caughtTimestamp,
      'started_hunt_timestamp': instance.startedHuntTimestamp,
      'catches': instance.catches?.map((e) => e.toJson()).toList(),
    };
